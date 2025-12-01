import flet as ft
import threading
import time
import datetime
import json
import os
import random
from cajaAzul import BlueBox
from configuracion import ConfiguracionContainer

class RelojGlobal:
    def __init__(self):
        self.horas_registradas = []
        self.archivo_horas = "horas.json"
        self.reloj_activo = True
        self.ultima_ejecucion = {}
        self.callbacks = []
        
        # Cargar horas guardadas
        self.cargar_horas()
        self.iniciar()

    def agregar_callback(self, callback):
        """Agrega una función que se ejecutará cuando suene una alarma"""
        self.callbacks.append(callback)

    def cargar_horas(self):
        """Carga las horas desde archivo JSON"""
        if os.path.exists(self.archivo_horas):
            try:
                with open(self.archivo_horas, "r") as file:
                    datos = json.load(file)
                    self.horas_registradas = [
                        datetime.datetime.strptime(h, "%H:%M").time()
                        for h in datos
                    ]
                print(f"RelojGlobal: Horas cargadas: {[h.strftime('%I:%M %p') for h in self.horas_registradas]}")
            except Exception as e:
                print(f"RelojGlobal: Error cargando horas: {e}")
                self.horas_registradas = []

    def guardar_horas(self):
        """Guarda las horas en archivo JSON"""
        try:
            datos = [h.strftime("%H:%M") for h in self.horas_registradas]
            with open(self.archivo_horas, "w") as file:
                json.dump(datos, file)
        except Exception as e:
            print(f"RelojGlobal: Error guardando horas: {e}")

    def agregar_hora(self, hora_time):
        """Agrega una hora a la lista global"""
        if hora_time not in self.horas_registradas:
            self.horas_registradas.append(hora_time)
            self.guardar_horas()
            print(f"RelojGlobal: Hora agregada: {hora_time.strftime('%I:%M %p')}")
            return True
        return False

    def eliminar_hora(self, hora_time):
        """Elimina una hora de la lista global"""
        if hora_time in self.horas_registradas:
            self.horas_registradas.remove(hora_time)
            self.guardar_horas()
            print(f"RelojGlobal: Hora eliminada: {hora_time.strftime('%I:%M %p')}")
            return True
        return False

    def iniciar(self):
        """Inicia el reloj global en un hilo separado"""
        if not hasattr(self, 'thread') or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            print("RelojGlobal: Iniciado")

    def _loop(self):
        """Loop principal del reloj"""
        while self.reloj_activo:
            try:
                ahora = datetime.datetime.now()
                
                # Revisar TODAS las horas guardadas
                for hora_obj in self.horas_registradas:
                    hora_actual_minuto = ahora.strftime("%I:%M %p")
                    segundos = ahora.strftime("%S")
                    hora_objetivo_str = hora_obj.strftime("%I:%M %p")

                    # Se ejecuta SOLO en el segundo 00
                    if hora_actual_minuto == hora_objetivo_str and segundos == "00":
                        h_obj = datetime.datetime.combine(ahora.date(), hora_obj)
                        clave = h_obj.strftime("%Y-%m-%d %H:%M")

                        if clave not in self.ultima_ejecucion:
                            self.ultima_ejecucion[clave] = True
                            self._ejecutar_alarma(hora_objetivo_str)
                            print(f"RelojGlobal: ✓ Alarma: {hora_objetivo_str}")

                time.sleep(1)
                
            except Exception as e:
                print(f"RelojGlobal: Error en loop: {e}")
                time.sleep(1)

    def _ejecutar_alarma(self, hora):
        """Ejecuta todos los callbacks registrados"""
        for callback in self.callbacks:
            try:
                callback(hora)
            except Exception as e:
                print(f"RelojGlobal: Error en callback: {e}")

    def detener(self):
        """Detiene el reloj global"""
        self.reloj_activo = False

class UI(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page
        
        # Variables para datos en tiempo real
        self.datos_tiempo_real = {
            'temperatura': 20,
            'humedad': 70, 
            'presion': 90,
            'frecuencia': 60
        }
        
        # Crear reloj global
        self.reloj_global = RelojGlobal()
        # Registrar callback para alarmas
        self.reloj_global.agregar_callback(self._on_alarma)
        
        self.color_teal = ft.Colors.GREY_300

        # PRIMERO inicializar todos los componentes
        self._initialize_ui_components()
        
        # LUEGO asignar el contenido
        self.content = self.resp_container

    def _on_alarma(self, hora):
        """Se ejecuta cuando el reloj global detecta una alarma"""
        print(f"UI: Alarma recibida: {hora}")
        # Aquí puedes mostrar notificaciones, etc.
        def mostrar_notificacion():
            d = ft.AlertDialog(
                title=ft.Text("¡Alarma!"),
                content=ft.Text(f"Hora programada: {hora}"),
                actions=[ft.TextButton("OK", on_click=lambda e: self.page.close(d))]
            )
            self.page.open(d)
        
        self.page.run_thread(mostrar_notificacion)

    def _initialize_ui_components(self):
        """Inicializa todos los componentes de la interfaz de usuario"""

        # Crear BlueBox y guardar referencias
        self.blue_box_temperatura = BlueBox(f"{self.datos_tiempo_real['temperatura']}°C", mostrar_boton=False, ancho=100, alto=100)
        self.blue_box_humedad = BlueBox(f"{self.datos_tiempo_real['humedad']}%", on_click_fn=self.accion_humedad)
        self.blue_box_presion = BlueBox(f"{self.datos_tiempo_real['presion']}Pa", on_click_fn=self.accion_presion)
        self.blue_box_frecuencia = BlueBox(f"{self.datos_tiempo_real['frecuencia']}Hz", on_click_fn=self.accion_frecuencia)
        
        # Guardar referencias en diccionario
        self.blue_boxes = {
            'temperatura': self.blue_box_temperatura,
            'humedad': self.blue_box_humedad,
            'presion': self.blue_box_presion,
            'frecuencia': self.blue_box_frecuencia
        }

        # Crear el ConfiguracionContainer con el reloj global
        self.config_container = ConfiguracionContainer(self.page, self.reloj_global)

        # Contenedores principales con contenido
        self.home_container_1 = ft.Container(
            bgcolor=self.color_teal,
            border_radius=20,
            expand=True,
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("Home", 
                            font_family="FontAwesome", 
                            size=15, 
                            weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(
                        border_radius=20,
                    )
                ]
            )
        )

        self.location_container_1 = ft.Container(
            bgcolor=self.color_teal,
            border_radius=20,
            expand=True,
            padding=20,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Ubicacion", 
                            font_family="FontAwesome", 
                            size=15, 
                            weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(
                        expand=True,
                        bgcolor="red",
                        border_radius=20,
                        alignment=ft.alignment.center,
                        content=ft.Column(
                            scroll=ft.ScrollMode.AUTO,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        self.blue_box_temperatura,
                                        self.blue_box_humedad,
                                        self.blue_box_presion,
                                        self.blue_box_frecuencia,
                                    ]
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Container(
                                            bgcolor="blue",
                                            border_radius=20,
                                            width=200,
                                            height=300,
                                        ),
                                        ft.Container(
                                            bgcolor="blue",
                                            border_radius=20,
                                            width=200,
                                            height=300,
                                        ),
                                        ft.Container(
                                            bgcolor="blue",
                                            border_radius=20,
                                            width=200,
                                            height=300,
                                        ),
                                        ft.Container(
                                            bgcolor="blue",
                                            border_radius=20,
                                            width=200,
                                            height=300,
                                        ),
                                    ]
                                ),
                            ]
                        )
                    )
                ]
            )
        )

        self.calendar_container_1 = ft.Container(
            bgcolor="green",
            alignment=ft.alignment.center,
            border_radius=20,
            expand=True,
            padding=20,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[self.config_container]
            )
        )

        self.setting_container_1 = ft.Container(
            bgcolor=self.color_teal,
            border_radius=20,
            expand=True,
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("Configuracion", 
                            font_family="FontAwesome", 
                            size=15, 
                            weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(
                        border_radius=20,
                    )
                ]
            )
        )

        self.container_list_1 = [
            self.home_container_1, 
            self.location_container_1, 
            self.calendar_container_1, 
            self.setting_container_1
        ]
        
        self.container_1 = ft.Container(content=self.container_list_1[0], expand=True)

        # BUTTON CONNECT
        self.btn_connect = ft.Container(
            width=130,
            height=50,
            bgcolor=ft.Colors.AMBER,
            border_radius=50,
            alignment=ft.alignment.center,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_hover=self.Check_On_Hover,
            content=ft.Text("Home"),
            on_click = lambda e: self.change_page_manual(0)
        )

        self.btn_connect2 = ft.Container(
            width=130,
            height=50,
            bgcolor=ft.Colors.AMBER,
            border_radius=50,
            alignment=ft.alignment.center,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_hover=self.Check_On_Hover,
            content=ft.Text("Location"),
            on_click = lambda e: self.change_page_manual(1)
        )

        self.btn_connect3 = ft.Container(
            width=130,
            height=50,
            bgcolor=ft.Colors.AMBER,
            border_radius=50,
            alignment=ft.alignment.center,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_hover=self.Check_On_Hover,
            content=ft.Text("Calendar"),
            on_click = lambda e: self.change_page_manual(2)
        )

        self.btn_connect4 = ft.Container(
            width=130,
            height=50,
            bgcolor=ft.Colors.AMBER,
            border_radius=50,
            alignment=ft.alignment.center,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_hover=self.Check_On_Hover,
            content=ft.Text("Setting"),
            on_click = lambda e: self.change_page_manual(3)
        )

        self.navigation_container = ft.Container(
            col=1.6,
            expand=True,
            bgcolor=self.color_teal,
            border_radius=10,
            padding=ft.padding.only(top=20),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                controls=[
                    self.btn_connect,
                    self.btn_connect2,
                    self.btn_connect3,
                    self.btn_connect4,
                ]
            )
        )

        self.frame_2 = ft.Container(
            col=10,
            alignment=ft.alignment.center,
            bgcolor="blue",
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    self.container_1,
                ]
            )   
        )
        
        # Layout responsivo principal
        self.resp_container = ft.ResponsiveRow(
            controls=[
                self.navigation_container,
                self.frame_2,
            ]
        )

        # Iniciar actualización de datos
        self.iniciar_actualizacion_datos()

    def iniciar_actualizacion_datos(self):
        """Inicia la actualización de datos en tiempo real"""
        def actualizar_datos():
            while True:
                try:
                    # Simular obtención de datos
                    nuevos_datos = self.obtener_datos_actualizados()
                    
                    # Actualizar el diccionario global
                    self.datos_tiempo_real.update(nuevos_datos)
                    
                    # Actualizar los BlueBox en el hilo principal
                    def actualizar_ui():
                        for clave, valor in nuevos_datos.items():
                            if clave in self.blue_boxes:
                                unidad = self.obtener_unidad(clave)
                                
                                # REDONDEAR ANTES DE MOSTRAR
                                if clave in ['temperatura', 'presion', 'frecuencia']:
                                    valor_redondeado = round(valor, 1)  # 1 decimal
                                else:
                                    valor_redondeado = round(valor)     # 0 decimales
                                
                                nuevo_texto = f"{valor_redondeado}{unidad}"
                                
                                bluebox = self.blue_boxes[clave]
                                # Usar el método actualizar_valor si existe
                                if hasattr(bluebox, 'actualizar_valor'):
                                    bluebox.actualizar_valor(nuevo_texto)
                                else:
                                    # Buscar y actualizar el texto principal
                                    self.actualizar_texto_bluebox(bluebox, nuevo_texto)
                        
                        self.page.update()
                    
                    self.page.run_thread(actualizar_ui)
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Error en actualización de datos: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=actualizar_datos, daemon=True)
        thread.start()

    def obtener_datos_actualizados(self):
        """Simula la obtención de datos actualizados con valores realistas"""
        nuevos_datos = {
            'temperatura': self.datos_tiempo_real['temperatura'] + random.uniform(-0.5, 0.5),
            'humedad': self.datos_tiempo_real['humedad'] + random.uniform(-2, 2),
            'presion': self.datos_tiempo_real['presion'] + random.uniform(-0.5, 0.5),
            'frecuencia': self.datos_tiempo_real['frecuencia'] + random.uniform(-0.2, 0.2)
        }
        
        # Limitar los valores dentro de rangos razonables
        nuevos_datos['temperatura'] = max(15, min(35, nuevos_datos['temperatura']))
        nuevos_datos['humedad'] = max(30, min(90, nuevos_datos['humedad']))
        nuevos_datos['presion'] = max(80, min(110, nuevos_datos['presion']))
        nuevos_datos['frecuencia'] = max(55, min(65, nuevos_datos['frecuencia']))
        
        return nuevos_datos

    def obtener_unidad(self, clave):
        """Devuelve la unidad correspondiente para cada dato"""
        unidades = {
            'temperatura': '°C',
            'humedad': '%',
            'presion': 'Pa',
            'frecuencia': 'Hz'
        }
        return unidades.get(clave, '')

    def actualizar_texto_bluebox(self, bluebox, nuevo_texto):
        """Busca y actualiza el texto principal de un BlueBox"""
        try:
            if hasattr(bluebox, 'content') and hasattr(bluebox.content, 'controls'):
                for control in bluebox.content.controls:
                    if isinstance(control, ft.Text):
                        # El texto principal es el que tiene tamaño 20
                        if control.size == 20 and control.weight == ft.FontWeight.BOLD:
                            control.value = nuevo_texto
                            return
        except Exception as e:
            print(f"Error actualizando BlueBox: {e}")

    def accion_temperatura(self, e):
        print("Botón de temperatura presionado")

    def accion_humedad(self, e):
        print("Botón de humedad presionado")

    def accion_presion(self, e):
        print("Botón de presión presionado")

    def accion_frecuencia(self, e):
        print("Botón de frecuencia presionado")

    def change_page_manual(self, index):
        self.container_1.content = self.container_list_1[index]
        self.update()

    def Check_On_Hover(self, e):
        ctrl = e.control
        is_hover = (e.data == "true" or e.data is True)

        if is_hover:
            ctrl.border = ft.border.all(3, ft.Colors.GREEN_700)
        else:
            ctrl.border = ft.border.all(2, ft.Colors.TRANSPARENT)
        ctrl.update()

    def will_unmount(self):
        """Detener el reloj global al cerrar la app"""
        self.reloj_global.detener()

def main(page: ft.Page):
    page.title = "Sistema de Monitoreo"
    page.window.width = 1316
    page.window.height = 570
    page.window.resizable = True
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.bgcolor = ft.Colors.TRANSPARENT

    ui = UI(page)
    page.add(ui)

if __name__ == "__main__":
    ft.app(target=main)