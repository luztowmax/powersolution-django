# HomePower — Django Edition

A Django replacement for the Flask HomePower prototype. Includes Django admin, SQLite models, battery chemistry filtering, solar sizing, equipment pricing, customer records and downloadable PDF quotations.

## Setup (Windows PowerShell)

1. Install Python 3.10+ and open this folder in VS Code.
2. In the VS Code terminal:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations energy
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ for the calculator and http://127.0.0.1:8000/admin/ for the built-in Django admin. Login with the superuser created above.

On macOS/Linux activate with `source venv/bin/activate` and use `python3` if needed.

## Administration

The Django admin lets you add/edit/delete appliances, inverters, batteries, solar panels, accessories, customers and quotations. Product prices are stored in SQLite (`db.sqlite3`) rather than JSON. Set battery chemistry on battery products; supported choices: Lithium, Tubular, Gel and AGM. Set battery voltage and Ah, inverter kVA, solar panel wattage, and accessory default quantity. The calculator filters batteries by chemistry and compatible nominal voltage.

## Moving from the Flask version

This project has a **new Django database**. The old Flask SQLite file cannot be directly substituted for `db.sqlite3`. To transfer real data, export and map records to Django models or create a one-off migration script. The demo seed is only an example; it does not import existing Flask customers or quotes.

## Security and engineering limitations

- This is a development starter, not production-ready. Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS` and configure HTTPS, production hosting, backups, logging, privacy controls and proper access permissions before deployment.
- Public quote creation and PDF links are provided for prototyping only. Before going live, add customer login or token-based quote access, rate limiting, and personal-data protection. Do not publish real customer data through guessable quotation IDs.
- Example NGN prices are illustrative, not live market quotes. Replace them in Django admin.
- Inverter sizing uses connected running watts, margin and power factor; it does not account for surge curves or specific inverter compatibility.
- Battery sizing assumes all selected appliances run for the full backup duration and uses user-selected depth of discharge. Check battery BMS, temperature, ageing, discharge current and manufacturer instructions.
- PV sizing uses daily Wh, peak sun hours and derating; verify solar irradiation, shading, panel strings, MPPT limits and controller requirements.
- Accessories and services use fixed catalogue default quantities, not a detailed bill of materials.
- The project uses Django built-in admin users; public customer signup/login is not yet implemented. Customer details are saved with quotations.
