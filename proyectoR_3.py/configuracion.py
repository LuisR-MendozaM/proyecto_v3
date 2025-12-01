import flet as ft
import datetime

class ConfiguracionContainer(ft.Container):
    def __init__(self, page=None, reloj_global=None):
        super().__init__(expand=True)

        self.page = page
        self.reloj_global = reloj_global  # Recibe el reloj global
        self.hora_objetivo = None

        # ---------- TIME PICKER ----------
        self.time_picker = ft.TimePicker(
            confirm_text="Aceptar",
            help_text="Selecciona una hora",
            on_change=self.hora_seleccionada,
        )
        
        if page:
            page.overlay.append(self.time_picker)

        # ---------- TEXTO HORA ACTUAL ----------
        self.texto_hora = ft.Text(
            value="--:-- --",
            size=28,
            weight="bold",
            color="black",
        )

        # ---------- BOTÓN ----------
        self.btn_seleccionar = ft.CupertinoButton(
            content=ft.Text("Seleccionar hora", size=11, color=ft.CupertinoColors.BLACK),
            width=130,
            height=48,
            bgcolor=ft.CupertinoColors.ACTIVE_BLUE,
            on_click=self.abrir_time_picker
        )

        # ---------- LISTA DE HORAS ----------
        self.lista_horas = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO)

        # Cargar horas desde el reloj global si existe
        self.actualizar_lista_horas()

        # ---------- INTERFAZ ----------
        self.content = ft.Container(
            bgcolor=ft.Colors.GREY_300,
            border_radius=20,
            width=400,
            height=400,
            padding=20,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        bgcolor="white",
                        height=100,
                        border_radius=20,
                        alignment=ft.alignment.center,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            controls=[self.texto_hora, self.btn_seleccionar]
                        )
                    ),
                    ft.Divider(height=9, thickness=3, color=ft.Colors.BLACK),
                    ft.Text("Horas registradas:", size=16, weight="bold"),
                    ft.Container(
                        bgcolor="white",
                        border_radius=20,
                        expand=True,
                        padding=10,
                        width=float("inf"),
                        content=self.lista_horas
                    )
                ]
            )
        )

        # Iniciar solo la actualización de la hora visual
        self.iniciar_actualizacion_hora_visual()

    def actualizar_lista_horas(self):
        """Actualiza la lista de horas desde el reloj global"""
        self.lista_horas.controls.clear()
        if self.reloj_global and hasattr(self.reloj_global, 'horas_registradas'):
            for hora_time in self.reloj_global.horas_registradas:
                hora_str = hora_time.strftime("%I:%M %p")
                fila = self.crear_fila_hora(hora_time, hora_str)
                self.lista_horas.controls.append(fila)

    def iniciar_actualizacion_hora_visual(self):
        """Solo actualiza la hora visual, no las alarmas"""
        import threading
        import time
        
        def actualizar_hora():
            while True:
                try:
                    ahora = datetime.datetime.now()
                    if self.page:
                        def update_ui():
                            self.texto_hora.value = ahora.strftime("%I:%M:%S %p")
                            self.page.update()
                        self.page.run_thread(update_ui)
                    time.sleep(1)
                except:
                    break
        
        thread = threading.Thread(target=actualizar_hora, daemon=True)
        thread.start()

    def abrir_time_picker(self, e):
        if self.page:
            self.page.open(self.time_picker)

    def hora_seleccionada(self, e):
        if e.control.value:
            self.hora_objetivo = e.control.value
            hora_formato = self.hora_objetivo.strftime("%I:%M %p")

            # Usar el reloj global para agregar la hora
            if self.reloj_global and hasattr(self.reloj_global, 'agregar_hora'):
                if self.reloj_global.agregar_hora(self.hora_objetivo):
                    print("Hora agregada globalmente:", hora_formato)
                    # Actualizar lista local
                    self.actualizar_lista_horas()
                    if self.page:
                        self.page.update()

    def crear_fila_hora(self, hora_time, hora_str):
        fila = ft.Container(
            padding=10,
            border_radius=8,
            bgcolor=ft.Colors.GREY_100,
        )

        fila.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(hora_str, size=16, color="black"),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color="red",
                    on_click=lambda e, hora=hora_time: self.eliminar_hora(hora)
                )
            ]
        )
        return fila

    def eliminar_hora(self, hora_time):
        """Elimina una hora usando el reloj global"""
        if self.reloj_global and hasattr(self.reloj_global, 'eliminar_hora'):
            if self.reloj_global.eliminar_hora(hora_time):
                self.actualizar_lista_horas()
                if self.page:
                    self.page.update()

    def mi_accion(self, hora):
        print(f"¡La hora {hora} ha sido alcanzada!")