# Path: mobile_app/ui/generators/list_gen.py
# Version: Kivy_1.0
# Description: Генератор списков (Checkboxes, Tags) на Kivy.

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.logger import Logger
from kivy.clock import Clock

from core import schema
from core.draft_manager import draft
from .base import BaseGenerator, CardBox

class ListGenerator(BaseGenerator):

    # ================= CHECKBOXES =================
    def render_checkboxes(self, config_list):
        # Оборачиваем все группы в один вертикальный контейнер
        container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        container.bind(minimum_height=container.setter('height'))
        
        for item in config_list:
            try:
                group = self._render_single_cb_group(item)
                container.add_widget(group)
            except Exception as e:
                Logger.error(f"[GEN ERROR] Checkbox group failed: {e}")
                
        return container

    def _render_single_cb_group(self, item):
        # 1. Resolve Keys
        key = item.get("list") or item.get("db_name")
        global_def = self.fas_config.get("checkboxes_list", {}).get(key, {})
        
        real_db_name = global_def.get("db_name", key)
        real_label = item.get("label_name") or global_def.get("label_name", key)
        
        # 2. UI Container (CardBox)
        card = CardBox(title=f"CHECKBOXES: {real_label}", bg_color=(1, 0.98, 0.9, 1)) # Amber-ish
        
        # Контейнер для строк (items)
        items_box = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        items_box.bind(minimum_height=items_box.setter('height'))
        card.add_widget(items_box)
        
        ui_key = f"checks_{real_db_name}"
        
        # --- Create Row Function ---
        def create_row(idx):
            full_name = f"{real_db_name}_{idx}"
            is_checked, ts = draft.get_checkbox_state(full_name)
            
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height='30dp', spacing=10)
            
            # Kivy CheckBox
            cb = CheckBox(size_hint_x=None, width='30dp', active=is_checked, color=(0,0,0,1))
            
            # Label with status
            lbl_text = f"{real_label} ({idx})"
            if ts: lbl_text += f" ({ts})"
            lbl = Label(text=lbl_text, color=(0,0,0,1), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            
            # Debug info
            lbl_debug = Label(text=f"[C_{full_name}]", color=(0.6,0.6,0.6,1), font_size='10sp', size_hint_x=0.3)
            
            # Logic
            def on_active(checkbox, value):
                timestamp = draft.toggle_checkbox(full_name, value)
                new_text = f"{real_label} ({idx})"
                if timestamp: new_text += f" ({timestamp})"
                lbl.text = new_text
                Logger.info(f"[UI LOG] Checkbox {full_name} set to {value}")

            cb.bind(active=on_active)
            
            row.add_widget(cb)
            row.add_widget(lbl)
            row.add_widget(lbl_debug)
            return row

        # 3. Init items
        default_count = item.get("number", 1)
        current_count = draft.get_ui_count(ui_key, default_count)
        
        for i in range(1, current_count + 1):
            items_box.add_widget(create_row(i))

        # 4. Buttons (+ / -)
        if item.get("add", False):
            btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=5)
            
            btn_add = Button(text="+", background_color=(0.2, 0.8, 0.2, 1))
            btn_rem = Button(text="-", background_color=(0.8, 0.2, 0.2, 1))
            
            def add_item(instance):
                curr = draft.get_ui_count(ui_key, default_count)
                curr += 1
                items_box.add_widget(create_row(curr))
                draft.set_ui_count(ui_key, curr)
                Logger.info(f"[UI LOG] Added checkbox row {curr}")

            def rem_item(instance):
                curr = draft.get_ui_count(ui_key, default_count)
                if curr > 1:
                    # Clean data
                    full_name = f"{real_db_name}_{curr}"
                    draft.toggle_checkbox(full_name, False)
                    
                    # Remove widget (last one)
                    if items_box.children:
                        # Kivy stores children in reverse order usually? 
                        # No, add_widget appends. children[0] is last added.
                        items_box.remove_widget(items_box.children[0]) 
                    
                    draft.set_ui_count(ui_key, curr - 1)
                    Logger.info(f"[UI LOG] Removed checkbox row {curr}")

            btn_add.bind(on_release=add_item)
            btn_rem.bind(on_release=rem_item)
            
            btn_row.add_widget(btn_add)
            btn_row.add_widget(btn_rem)
            card.add_widget(btn_row)

        return card

    # ================= TAGS =================
    def render_tags(self, config_list):
        container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        container.bind(minimum_height=container.setter('height'))
        
        for item in config_list:
            try:
                group = self._render_single_tag_group(item)
                container.add_widget(group)
            except Exception as e:
                Logger.error(f"[GEN ERROR] Tag group failed: {e}")
                
        return container

    def _render_single_tag_group(self, item):
        ln = item.get("list")
        cfg = self.fas_config.get("tag_lists", {}).get(ln, {})
        # Fallback
        if not cfg: 
            cfg = {"label_name": item.get("label_name", ln), "db_name": ln.upper(), "value": {}}

        prefix = cfg.get("db_name")
        if not prefix.endswith("_"): prefix += "_"
        
        val_cfg = cfg.get("value", {})
        
        card = CardBox(title=f"TAGS: {cfg.get('label_name')}", bg_color=(0.9, 1, 0.9, 1)) # Light Green
        items_box = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        items_box.bind(minimum_height=items_box.setter('height'))
        card.add_widget(items_box)
        
        ui_key = f"tags_{ln}"

        # --- Create Row Function ---
        def create_tag_row(idx):
            full_name = f"{prefix}{idx}"
            label_txt = f"{cfg.get('label_name')} ({idx})"
            saved_val = draft.get_tag_value(full_name)
            
            # Row Container
            row_cont = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2)
            row_cont.bind(minimum_height=row_cont.setter('height')) # Dynamic height for tree
            
            # 1. Simple List
            if "list_range" in val_cfg:
                row_cont.height = '40dp'
                line = BoxLayout(orientation='horizontal')
                
                lr = val_cfg["list_range"]
                vals = [str(x) for x in range(lr[0], lr[1], lr[2])]
                
                # Если сохраненного значения нет в списке, Spinner покажет первый элемент
                # Но нам нужно показать "пусто" или сохраненное.
                # Kivy Spinner text по умолчанию - первый элемент values.
                
                sp_text = saved_val if saved_val in vals else (vals[0] if vals else "")
                
                spinner = Spinner(text=sp_text, values=vals, size_hint_x=0.7)
                
                def on_spin_select(inst, text):
                    draft.update_tag(full_name, text)
                    Logger.info(f"[UI LOG] Tag {full_name} set to {text}")
                
                # Если есть сохраненное значение, но spinner его не знает (например очищено), 
                # spinner.text не обновит draft. Поэтому при инициализации не дергаем draft.
                # Но bind сработает при изменении.
                spinner.bind(text=on_spin_select)
                
                # Кнопка очистки
                btn_clr = Button(text="X", size_hint_x=0.15, background_color=(1, 0.7, 0.7, 1))
                def clear_tag(inst):
                    spinner.text = vals[0] # Reset visual (Kivy spinner can't be empty text easily without hack)
                    # Но мы можем просто записать пустую строку в базу
                    draft.update_tag(full_name, "")
                btn_clr.bind(on_release=clear_tag)
                
                line.add_widget(Label(text=label_txt, color=(0,0,0,1), size_hint_x=0.3))
                line.add_widget(spinner)
                line.add_widget(btn_clr)
                row_cont.add_widget(line)

            # 2. Tree Logic (Complex)
            elif "type" in val_cfg and val_cfg["type"] == "tree":
                # Контейнер для спиннеров
                stack = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2)
                stack.bind(minimum_height=stack.setter('height'))
                
                row_cont.add_widget(Label(text=label_txt, color=(0,0,0,1), size_hint_y=None, height='20dp', bold=True))
                row_cont.add_widget(stack)
                
                # Чтобы высота row_cont подстраивалась под stack
                def update_height(*args):
                    row_cont.height = stack.height + 30 # + label height + spacing
                stack.bind(height=update_height)

                root_node = self.fas_config.get("category", {}).get("main", {}).get("children", {})
                
                # Рекурсивная функция
                def build_level(node_dict, chain_vals):
                    if not node_dict: return
                    
                    opts = list(node_dict.keys())
                    current_val = chain_vals[0] if chain_vals else "Select..."
                    remaining = chain_vals[1:] if chain_vals else []
                    
                    sp = Spinner(text=current_val, values=opts, size_hint_y=None, height='40dp')
                    
                    def on_select(inst, text):
                        if text == "Select...": return
                        
                        # Найти индекс этого спиннера
                        try: idx_in_stack = stack.children.index(inst) # children are reversed in Kivy by default?
                        # В Kivy children[0] это последний добавленный.
                        # Нам нужно найти его и удалить всех кто ДОБАВЛЕН ПОЗЖЕ (выше в списке children, но ниже визуально).
                        # Stack: [spin1 (bottom), spin2, spin3 (top)] <-- add_widget добавляет наверх по умолчанию?
                        # Нет, в BoxLayout по умолчанию добавляет в конец списка (справа/снизу), но index 0 это последний.
                        # Проще: очистим все виджеты, которые были добавлены ПОСЛЕ текущего.
                        except: return 
                        
                        # Удаляем детей, которые были добавлены ПОСЛЕ (т.е. имеют меньший индекс в списке children, если добавляли в конец)
                        # Но BoxLayout.add_widget добавляет в index 0. Значит предыдущие уровни имеют БОЛЬШИЙ индекс.
                        # Следующие уровни имеют МЕНЬШИЙ индекс.
                        
                        # Удаляем всех детей с индексом < текущего
                        # children = [Level3, Level2, Level1] (Level3 added last)
                        # Если меняем Level1 (index 2), надо удалить Level2 (1) и Level3 (0).
                        
                        children_to_remove = [c for c in stack.children if stack.children.index(c) < idx_in_stack]
                        for c in children_to_remove:
                            stack.remove_widget(c)
                            
                        # Строим следующий уровень
                        nxt = node_dict.get(text, {}).get("children", {})
                        if nxt:
                            build_level(nxt, [])
                        
                        # Сохраняем путь
                        # Нужно собрать значения в ПРАВИЛЬНОМ порядке (от корня)
                        # children = [Level3, Level2, Level1] -> reverse -> [L1, L2, L3]
                        vals = [c.text for c in reversed(stack.children) if c.text != "Select..."]
                        full_path = "/".join(vals)
                        draft.update_tag(full_name, full_path)
                        Logger.info(f"[UI LOG] Tree tag update: {full_path}")

                    sp.bind(text=on_select)
                    
                    # Добавляем в стек. add_widget добавляет в начало списка (index 0).
                    # Визуально в BoxLayout (vertical) index 0 рисуется ПОСЛЕДНИМ (снизу), если не менять поряок?
                    # Нет, в Kivy index 0 рисуется ПЕРВЫМ (сверху) если не задано иное?
                    # Обычно add_widget добавляет на экран поверх/после. 
                    # Проверим на практике: add_widget adds to list[0].
                    # BoxLayout рисует [n, ..., 1, 0].
                    # Чтобы уровни шли сверху вниз: L1, L2...
                    # Нам нужно добавлять L2 так, чтобы он был ПОСЛЕ L1.
                    # stack.add_widget(sp) -> L1. children=[L1]
                    # stack.add_widget(sp2) -> L2. children=[L2, L1]. Draws L2 then L1? No.
                    # BoxLayout (vertical) рисует children[-1] сверху, children[0] снизу.
                    # Значит L1 (oldest) должен быть в конце списка.
                    # add_widget добавляет в index 0. Значит список [New, Old].
                    # Значит New рисуется СНИЗУ. Это то, что нам надо для дерева (рост вниз).
                    
                    stack.add_widget(sp)
                    
                    if current_val in node_dict:
                        build_level(node_dict[current_val].get("children", {}), remaining)

                # Init
                chain = saved_val.split("/") if saved_val else []
                build_level(root_node, chain)

            # 3. Manual (TextInput)
            else:
                row_cont.height = '40dp'
                line = BoxLayout(orientation='horizontal')
                
                ti = TextInput(text=saved_val, multiline=False, write_tab=False, hint_text=label_txt)
                ti.bind(text=lambda inst, val: draft.update_tag(full_name, val))
                
                line.add_widget(ti)
                line.add_widget(Label(text=f"[T_{full_name}]", font_size='10sp', size_hint_x=0.3, color=(0.5,0.5,0.5,1)))
                row_cont.add_widget(line)

            return row_cont

        # 3. Init items
        default_count = item.get("number", 1)
        current_count = draft.get_ui_count(ui_key, default_count)
        
        for i in range(1, current_count + 1):
            items_box.add_widget(create_tag_row(i))

        # 4. Buttons
        if item.get("add", False):
            btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=5)
            btn_add = Button(text="+", background_color=(0.2, 0.8, 0.2, 1))
            btn_rem = Button(text="-", background_color=(0.8, 0.2, 0.2, 1))
            
            def add_t(inst):
                curr = draft.get_ui_count(ui_key, default_count) + 1
                items_box.add_widget(create_tag_row(curr))
                draft.set_ui_count(ui_key, curr)

            def rem_t(inst):
                curr = draft.get_ui_count(ui_key, default_count)
                if curr > 1:
                    draft.update_tag(f"{prefix}{curr}", "")
                    if items_box.children: items_box.remove_widget(items_box.children[0])
                    draft.set_ui_count(ui_key, curr - 1)
            
            btn_add.bind(on_release=add_t)
            btn_rem.bind(on_release=rem_t)
            btn_row.add_widget(btn_add)
            btn_row.add_widget(btn_rem)
            card.add_widget(btn_row)

        return card