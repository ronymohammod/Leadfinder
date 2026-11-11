# LeadFinder

🔎 LeadFinder – Automated Business Lead Generation

LeadFinder is an automated lead generation tool built with Python and Django. It helps users find relevant business websites based on a search topic, extract publicly available email addresses and phone numbers, validate email syntax and domain MX records, and generate downloadable lead lists in CSV format.

The project uses a free and open-source technology stack and does not require any paid API keys.

✨ Features
🔍 Automated Website Search: Finds relevant websites based on user-provided topics using DuckDuckGo public HTML search results.
📧 Email Extraction: Extracts publicly available email addresses from target websites.
📞 Phone Number Extraction: Collects publicly available phone numbers.
✅ Email Validation: Checks email syntax and verifies whether the domain has valid MX records.
📊 Lead Management: Stores collected leads in a database.
📁 CSV Export: Downloads generated lead lists as CSV files.
⚙️ Background Processing: Uses Celery and Redis to perform scraping and validation tasks asynchronously.
🖥️ Web Interface: Simple Django-based interface for submitting search topics and viewing results.
🔐 Admin Dashboard: Manage search jobs and leads through Django Admin.
🛠️ Technology Stack
Technology	Purpose
Python	Core programming language
Django	Backend web framework
SQLite	Database
Celery	Background task processing
Redis	Celery message broker
BeautifulSoup	HTML parsing and data extraction
Requests	HTTP requests
DuckDuckGo HTML	Website search
DNS Resolver	Email domain MX validation
CSV	Lead data export
📂 Project Structure
text
leadfinder/
│
├── leadfinder/
│   ├── settings.py
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
│
├── leads/
│   ├── models.py
│   ├── forms.py
│   ├── tasks.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│
├── requirements.txt
├── manage.py
└── README.md

⚙️ Installation & Setup
1. Clone the Repository
bash
git clone https://github.com/ronymohammod/Leadfinder.git
cd Leadfinder

2. Create a Virtual Environment

Windows:

bash
python -m venv venv
venv\Scripts\activate


Linux / macOS:

bash
python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
bash
pip install -r requirements.txt

4. Install and Run Redis

Redis is required as the Celery message broker.

Windows (Docker):

bash
docker run -d --name leadfinder-redis -p 6379:6379 redis


Ubuntu / Debian:

bash
sudo apt install redis-server
sudo systemctl start redis-server


macOS:

bash
brew install redis
brew services start redis

5. Apply Database Migrations
bash
python manage.py migrate

6. Create an Admin Account (Optional)
bash
python manage.py createsuperuser

🚀 Running the Application

You need two separate terminals to run the application.

Terminal 1 – Start Django Server
bash
venv\Scripts\activate
python manage.py runserver

Terminal 2 – Start Celery Worker
bash
venv\Scripts\activate
celery -A leadfinder worker --loglevel=info

7. Open the Application

Visit:

http://127.0.0.1:8000/

📖 How to Use
Open the LeadFinder web application.
Enter a business topic or niche in the search field.
Submit the search request.
LeadFinder searches for relevant websites.
Publicly available email addresses and phone numbers are extracted.
Email syntax and domain MX records are checked.
View the generated leads.
Export the results as a CSV file.

Example Search Topics:

Furniture shops in Chittagong
Digital marketing agencies in Bangladesh
Real estate companies in Dhaka
Software development companies
Restaurants in London
⚙️ Configuration

You can customize the maximum number of websites checked per search through the Django settings file.

Open:

text
leadfinder/settings.py


Look for:

python
LEADFINDER_MAX_RESULTS


Change its value according to your requirements.

📧 Email Validation – Important Note

LeadFinder performs basic email validation using two checks:

Syntax Validation: Checks whether an email address follows the correct format.
MX Record Validation: Checks whether the email domain has mail exchange records.

Important: These checks do not confirm that a specific mailbox exists, is active, or can receive emails. They do not guarantee email deliverability.

⚠️ Limitations & Responsible Usage
LeadFinder uses DuckDuckGo's public HTML search pages instead of an official search API.
Excessive search requests may result in temporary rate limiting or blocking.
Search results may vary depending on availability and search engine behavior.
Only publicly accessible website information is collected.
Private databases, accounts, and restricted information are not accessed.
A 0.5-second delay is used between target website requests to reduce server load.
Always respect website Terms of Service, robots.txt policies, applicable privacy laws, and data protection regulations.
Use collected contact information responsibly and comply with applicable anti-spam requirements.
🔮 Future Improvements

Potential future enhancements include:

Integration with Google Programmable Search Engine.
More reliable search provider integration.
Advanced email verification services.
PostgreSQL database support.
Improved scraping error handling.
Production deployment with proper security settings.
Advanced lead filtering and categorization.
Improved dashboard and analytics.
🔒 Production Deployment

Before deploying to production:

Replace SQLite with PostgreSQL if required.
Set DEBUG = False.
Configure proper ALLOWED_HOSTS.
Use environment variables for sensitive settings.
Configure HTTPS.
Secure Redis and database connections.
Follow applicable privacy and data protection regulations.
💰 Cost & API Requirements

LeadFinder is designed around a free and open-source stack.

No paid API key is required for the default search implementation.
No paid email validation API is required.
Redis and Celery handle background processing.
Python and Django provide the application framework.

Third-party infrastructure or hosting may still incur costs.

👨‍💻 Author

Rony Mohammad

GitHub: @ronymohammod

Project Repository: LeadFinder

📄 License

This project is intended for educational and responsible business research purposes.

Add an appropriate open-source license file (such as MIT) before distributing the project under an open-source license.

⭐ If you find this project useful, consider starring the repository!



