import subprocess
import json
import sys
from pathlib import Path
 
#  Paramètres à ajuster
IAC_DIR = "C:\\Users\\phadj\\.aws"         # Dossier contenant vos fichiers IaC (CloudFormation, Terraform, etc.)
OUTPUT_FILE = "trivy_iac_report.json"
SEVERITIES = ["MEDIUM", "HIGH", "CRITICAL"]
 
def run_trivy_scan(iac_dir, output_file, severities):
    cmd = [
        "trivy",
        "config",
        iac_dir,
        "--severity", ",".join(severities),
        "--format", "json",
        "--output", output_file
    ]
    print(f" Lancement du scan Trivy : {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and result.returncode != 2:
        # Trivy peut retourner 2 si des vulnérabilités trouvées
        print(" Trivy a renvoyé un code de sortie non prévu :", result.returncode)
        print("STDERR :", result.stderr)
        sys.exit(result.returncode)
    print(" Scan terminé. Résultat enregistré dans", output_file)
 
def parse_report(output_file):
    path = Path(output_file)
    if not path.exists():
        print(" Le fichier de rapport n’a pas été trouvé :", output_file)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    findings = data.get("Results", [])
    summary = {sev: 0 for sev in SEVERITIES}
    for res in findings:
        vulnerabilities = res.get("Misconfigurations", []) + res.get("Vulnerabilities", [])
        for vuln in vulnerabilities:
            sev = vuln.get("Severity", "").upper()
            if sev in summary:
                summary[sev] += 1
    print("\n Résumé des vulnérabilités par sévérité :")
    for sev in SEVERITIES:
        print(f"  {sev:8s} : {summary[sev]}")
    return summary
 
def main():
    run_trivy_scan(IAC_DIR, OUTPUT_FILE, SEVERITIES)
    parse_report(OUTPUT_FILE)
 
if __name__ == "__main__":
    main()