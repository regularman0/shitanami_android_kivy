# Path: mobile_app/ui/generators/time_gen.py
# Version: Kivy_1.0
# Description: Генератор времени (Range/Duration) на Kivy.

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.logger import Logger

from datetime import datetime
from core import schema
from core.database import db
from core.draft_manager import draft
from .base import BaseGenerator, CardBox

class TimeGenerator(BaseGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ссылки на виджеты для обновления
        self.ti_start = None
        self.ti_end = None
        self.lbl_diff = None
        self.spinner_val = None
        
        self.is_duration_mode = False

    def set_mode(self, is_duration):
        self.is_duration_mode = is_duration
        Logger.info(f"[UI LOG] TimeGenerator mode set to: {'Duration' if is_duration else 'Range'}")

    # ================= RANGE =================
    def render_range(self, config):
        card = CardBox(title="RANGE", bg_color=(0.9, 0.95, 1, 1)) # Голубой фон
        
        # 1. Inputs Row
        row_inputs = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=5)
        
        s, e = draft.get_range()
        
        self.ti_start = TextInput(text=s, hint_text="Start", multiline=False)
        self.ti_start.bind(focus=self._on_focus_loss) # Сохраняем при потере фокуса
        
        btn_clr_s = Button(text="X", size_hint_x=None, width='30dp', background_color=(1, 0.5, 0.5, 1))
        btn_clr_s.bind(on_release=lambda x: self._clear_field('start'))

        self.ti_end = TextInput(text=e, hint_text="End", multiline=False)
        self.ti_end.bind(focus=self._on_focus_loss)

        btn_clr_e = Button(text="X", size_hint_x=None, width='30dp', background_color=(1, 0.5, 0.5, 1))
        btn_clr_e.bind(on_release=lambda x: self._clear_field('end'))

        row_inputs.add_widget(self.ti_start)
        row_inputs.add_widget(btn_clr_s)
        row_inputs.add_widget(self.ti_end)
        row_inputs.add_widget(btn_clr_e)
        
        card.add_widget(row_inputs)

        # 2. Copy Last Button
        btn_copy = Button(text="⬇ Copy Last End to Start ⬇", size_hint_y=None, height='40dp')
        btn_copy.bind(on_release=self._copy_last)
        card.add_widget(btn_copy)

        # 3. Math Config (Spinners)
        row_cfg = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=5)
        
        step_opts = config.get("step_options", [5, 60, 5])
        vals_step = [str(x) for x in range(*step_opts)]
        
        sp_step = Spinner(text=vals_step[0], values=vals_step, size_hint_x=0.4)
        # Динамический список значений
        self.spinner_val = Spinner(text='5', values=['5', '10', '15', '30'], size_hint_x=0.6)
        
        def on_step_select(spinner, text):
            step = int(text)
            self.spinner_val.values = [str(x) for x in range(step, 61, step)]
            self.spinner_val.text = str(step)
            
        sp_step.bind(text=on_step_select)
        on_step_select(None, sp_step.text) # Init

        row_cfg.add_widget(Label(text="Step:", color=(0,0,0,1), size_hint_x=0.2))
        row_cfg.add_widget(sp_step)
        row_cfg.add_widget(Label(text="Val:", color=(0,0,0,1), size_hint_x=0.2))
        row_cfg.add_widget(self.spinner_val)
        card.add_widget(row_cfg)

        # 4. Math Buttons
        # Grid 2x1 for Start and End controls
        grid = GridLayout(cols=2, spacing=5, size_hint_y=None, height='80dp')
        
        # Start Block
        box_s = BoxLayout(orientation='vertical')
        box_s.add_widget(Label(text="Start Controls", color=(0,0,0,1), font_size='10sp'))
        row_s_btns = BoxLayout(orientation='horizontal')
        
        btn_now_s = Button(text="Now")
        btn_now_s.bind(on_release=lambda x: self._set_now('start'))
        
        btn_sub_s = Button(text="-")
        btn_sub_s.bind(on_release=lambda x: self._do_math('start', 'sub'))
        
        btn_add_s = Button(text="+")
        btn_add_s.bind(on_release=lambda x: self._do_math('start', 'add'))
        
        row_s_btns.add_widget(btn_now_s)
        row_s_btns.add_widget(btn_sub_s)
        row_s_btns.add_widget(btn_add_s)
        box_s.add_widget(row_s_btns)
        
        # End Block
        box_e = BoxLayout(orientation='vertical')
        box_e.add_widget(Label(text="End Controls", color=(0,0,0,1), font_size='10sp'))
        row_e_btns = BoxLayout(orientation='horizontal')
        
        btn_now_e = Button(text="Now")
        btn_now_e.bind(on_release=lambda x: self._set_now('end'))
        
        btn_sub_e = Button(text="-")
        btn_sub_e.bind(on_release=lambda x: self._do_math('end', 'sub'))
        
        btn_add_e = Button(text="+")
        btn_add_e.bind(on_release=lambda x: self._do_math('end', 'add'))
        
        row_e_btns.add_widget(btn_now_e)
        row_e_btns.add_widget(btn_sub_e)
        row_e_btns.add_widget(btn_add_e)
        box_e.add_widget(row_e_btns)

        grid.add_widget(box_s)
        grid.add_widget(box_e)
        card.add_widget(grid)

        return card

    # ================= DURATION =================
    def render_duration(self, config):
        card = CardBox(title="DURATION", bg_color=(0.95, 0.9, 1, 1)) # Фиолетовый фон
        
        # Config Row
        row_cfg = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=5)
        
        s_opts = config.get("step_options", [5, 125, 5])
        def_val = config.get("defaults", {}).get("value", 30)
        
        sp_step = Spinner(text=str(s_opts[0]), values=[str(x) for x in range(*s_opts)], size_hint_x=0.3)
        sp_val = Spinner(text=str(def_val), values=[], size_hint_x=0.3)
        
        def on_step(inst, text):
            step = int(text)
            sp_val.values = [str(x) for x in range(step, 181, step)]
            if str(def_val) in sp_val.values: sp_val.text = str(def_val)
            else: sp_val.text = text
        sp_step.bind(text=on_step)
        on_step(None, sp_step.text)

        row_cfg.add_widget(Label(text="Step:", color=(0,0,0,1), size_hint_x=0.2))
        row_cfg.add_widget(sp_step)
        row_cfg.add_widget(Label(text="Val:", color=(0,0,0,1), size_hint_x=0.2))
        row_cfg.add_widget(sp_val)
        card.add_widget(row_cfg)

        # Actions Row
        row_act = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=5)
        
        btn_update = Button(text="UPDATE", background_color=(0.4, 0.2, 0.6, 1))
        
        self.lbl_diff = Label(text="Diff: --", color=(0,0,0,1), bold=True)
        self.lbl_fix = Label(text="", color=(0.5,0.5,0.5,1), font_size='10sp')
        
        def apply_dur(btn):
            try: mins = int(sp_val.text)
            except: mins = 30
            ns, ne = draft.sync_duration(mins)
            
            # Обновляем UI
            if self.ti_start: self.ti_start.text = ns
            if self.ti_end: self.ti_end.text = ne
            
            self.lbl_fix.text = f"Fix: {datetime.now().strftime('%H:%M')}"
            self._update_diff_label()
            
        btn_update.bind(on_release=apply_dur)
        
        row_act.add_widget(btn_update)
        row_act.add_widget(self.lbl_diff)
        row_act.add_widget(self.lbl_fix)
        card.add_widget(row_act)
        
        self._update_diff_label() # Init
        return card

    # ================= LOGIC HANDLERS =================
    
    def _on_focus_loss(self, instance, value):
        """Если фокус потерян (value=False), сохраняем значение"""
        if not value:
            target = "start" if instance == self.ti_start else "end"
            Logger.info(f"[UI LOG] Manual entry for {target}: {instance.text}")
            if draft.set_manual_time(target, instance.text):
                instance.background_color = (1, 1, 1, 1) # OK
                self._update_diff_label()
            else:
                instance.background_color = (1, 0.8, 0.8, 1) # Error

    def _clear_field(self, target):
        if target == "start":
            self.ti_start.text = ""
            draft.set_range("", self.ti_end.text)
        else:
            self.ti_end.text = ""
            draft.set_range(self.ti_start.text, "")
        self._update_diff_label()

    def _copy_last(self, btn):
        val = db.get_last_range_end()
        if not val and self.ti_end: val = self.ti_end.text
        if val:
            self.ti_start.text = val
            draft.set_range(val, self.ti_end.text)
            self._update_diff_label()

    def _set_now(self, target):
        now = datetime.now().strftime(schema.DT_FMT)
        if target == 'start':
            self.ti_start.text = now
            draft.set_range(now, self.ti_end.text)
        else:
            self.ti_end.text = now
            draft.set_range(self.ti_start.text, now)
        self._update_diff_label()

    def _do_math(self, target, op):
        try: mins = int(self.spinner_val.text)
        except: mins = 5
        
        if target == 'end' and self.is_duration_mode:
            ns, ne = draft.shift_range(mins, op)
        else:
            op_arg = op
            draft.modify_one_bound(target, mins, op_arg)
            ns, ne = draft.get_range()
            
        self.ti_start.text = ns
        self.ti_end.text = ne
        self._update_diff_label()

    def _update_diff_label(self):
        if not self.lbl_diff: return
        s, e = draft.get_range()
        try:
            d1 = datetime.strptime(s, schema.DT_FMT)
            d2 = datetime.strptime(e, schema.DT_FMT)
            diff = int((d2 - d1).total_seconds() / 60)
            self.lbl_diff.text = f"Diff: {diff}m"
        except:
            self.lbl_diff.text = "Diff: --"