import subprocess
import json
import os

class GoogleCloudSoldier:
    """
    Legión OVRIC - Soldado de Datos (Google Cloud Explorer)
    Misión: Integrar las capacidades de BigQuery y Dataproc en el Orbe.
    """
    
    def __init__(self):
        self.name = "GoogleCloudSoldier"
        self.status = "INITIALIZING"
        self.project_id = None
        
    def check_auth(self):
        """Verifica si gcloud está autenticado."""
        try:
            result = subprocess.run(["gcloud", "auth", "list", "--format=json"], 
                                 capture_output=True, text=True, check=True)
            auths = json.loads(result.stdout)
            if not auths:
                return False, "No hay cuentas autenticadas."
            return True, auths
        except Exception as e:
            return False, str(e)

    def get_projects(self):
        """Lista los proyectos disponibles."""
        try:
            result = subprocess.run(["gcloud", "projects", "list", "--format=json"], 
                                 capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            return {"error": str(e)}

    def query_bigquery(self, query):
        """Ejecuta una consulta en BigQuery."""
        try:
            # Usar bq command line tool que viene con el SDK
            result = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--format=json", query], 
                                 capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            return {"error": str(e)}

    def get_dataproc_clusters(self, region="us-central1"):
        """Lista los clusters de Dataproc."""
        try:
            result = subprocess.run(["gcloud", "dataproc", "clusters", "list", f"--region={region}", "--format=json"], 
                                 capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            return {"error": str(e)}

    def get_status_report(self):
        """Genera un reporte de salud del soldado."""
        auth_ok, info = self.check_auth()
        return {
            "soldier": self.name,
            "status": "ACTIVE" if auth_ok else "RECONNAISSANCE",
            "auth": info if auth_ok else "REQUIRED",
            "capabilities": ["BigQuery", "Dataproc", "Storage"]
        }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", help="Consulta SQL para BigQuery")
    parser.add_argument("--status", action="store_true", help="Obtener reporte de estado")
    args = parser.parse_ok = parser.parse_args()
    
    soldier = GoogleCloudSoldier()
    
    if args.query:
        print(json.dumps(soldier.query_bigquery(args.query)))
    else:
        print(json.dumps(soldier.get_status_report(), indent=2))
