package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"time"
)

// Soldado Rayo: Unidad de élite de Verix en Go.
// Misión: Alto rendimiento y mínima latencia.

type Mission struct {
	ID        string                 `json:"id"`
	Tarea     string                 `json:"tarea"`
	Params    map[string]interface{} `json:"parametros"`
	Timestamp string                 `json:"timestamp_inicio"`
}

type Result struct {
	Status    string                 `json:"status"`
	Timestamp string                 `json:"timestamp_fin"`
	Data      map[string]interface{} `json:"data"`
}

const (
	ID_SOLDADO = "Soldado_Rayo_01"
	LOG_PATH   = `c:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\orbe_log.txt`
)

func logMision(mensaje string, prioridad string) {
	timestamp := time.Now().Format("2006-01-02 15:04:05")
	entry := fmt.Sprintf("%s | %-10s | %-25s | %s\n", timestamp, prioridad, ID_SOLDADO, mensaje)
	f, err := os.OpenFile(LOG_PATH, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err == nil {
		f.WriteString(entry)
		f.Close()
	}
}

func main() {
	if len(os.Args) < 2 {
		logMision("Soldado Rayo activado sin ticket. Esperando órdenes.", "AVISO")
		return
	}

	ticketPath := os.Args[1]
	data, err := ioutil.ReadFile(ticketPath)
	if err != nil {
		logMision(fmt.Sprintf("Error leyendo ticket: %v", err), "CRITICO")
		return
	}

	var m Mission
	if err := json.Unmarshal(data, &m); err != nil {
		logMision(fmt.Sprintf("Error parseando ticket: %v", err), "CRITICO")
		return
	}

	logMision(fmt.Sprintf("Iniciando misión relámpago [%s]: %s", m.ID, m.Tarea), "ACCION")

	// Simulación de Cálculo de Alto Rendimiento
	start := time.Now()
	count := 0
	for i := 0; i < 1000000; i++ {
		count += i
	}
	elapsed := time.Since(start)

	res := Result{
		Status:    "exito",
		Timestamp: time.Now().Format(time.RFC3339),
		Data: map[string]interface{}{
			"motor":         "Go 1.24",
			"batch_process": "INTEGRITY_CHECK",
			"calculo_sum":   count,
			"latencia_ms":  elapsed.Seconds() * 1000,
		},
	}

	resData, _ := json.MarshalIndent(res, "", "    ")
	resPath := ticketPath[:len(ticketPath)-len(".json")] + "_resultado.json"
	ioutil.WriteFile(resPath, resData, 0644)

	logMision(fmt.Sprintf("Misión [%s] completada en %v. Corona entregada.", m.ID, elapsed), "EXITO")
}
