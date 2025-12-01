import threading
import time
import datetime
import json
import os

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