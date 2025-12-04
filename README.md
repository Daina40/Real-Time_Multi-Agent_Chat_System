Backend (Django)
Create virtual environment:
python -m venv venv
source venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Apply migrations:
python manage.py migrate

Start Django development server:
python manage.py runserver

Frontend (Next.js)
Install dependencies:
cd frontend_app
npm install

Run development server:
npm run dev

Open in browser:
Agent page: http://localhost:3000/agent
Visitor page: http://localhost:3000/visitor
