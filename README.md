# LeadFinder

টপিক দিলে অটোমেটিক ইন্টারনেট থেকে প্রাসঙ্গিক ওয়েবসাইট খুঁজে, ইমেইল/ফোন বের করে, ইমেইল
ভ্যালিডিটি চেক করে লিড লিস্ট বানিয়ে দেয়। পুরোটা ফ্রি/ওপেন-সোর্স স্ট্যাকে বানানো —
কোনো পেইড API key লাগে না।

## এটা আসলে কী করে, কী করে না (পড়ে নিও)

- এটা **DuckDuckGo-র পাবলিক HTML পেজ স্ক্র্যাপ করে সার্চ রেজাল্ট বের করে** — কোনো
  অফিশিয়াল API ব্যবহার করে না। বেশি দ্রুত/বেশি সংখ্যায় রিকোয়েস্ট পাঠালে DuckDuckGo
  সাময়িকভাবে ব্লক করতে পারে।
- ইমেইল "ভ্যালিড" মানে: সিনট্যাক্স ঠিক আছে এবং ডোমেইনের মেইল সার্ভার (MX record)
  আছে। এর মানে এই **না** যে মেইলবক্সটা অ্যাক্টিভ বা কেউ আসলে চেক করে — এটা একটা
  বেসিক স্যানিটি চেক, ১০০% ডেলিভারেবিলিটি গ্যারান্টি না।
- শুধু public ওয়েবসাইটে যে ইমেইল/ফোন খোলা আছে সেগুলোই তুলে আনে — কোনো প্রাইভেট ডেটা
  অ্যাক্সেস করে না।
- প্রতিটা টার্গেট সাইটে হালকা delay (0.5s) রাখা আছে যেন কোনো সাইটে চাপ না পড়ে —
  দায়িত্বশীলভাবে ব্যবহার করো।

## Setup (একবারই করতে হবে)

```bash
# 1) ভার্চুয়াল এনভায়রনমেন্ট বানাও
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2) ডিপেন্ডেন্সি ইনস্টল করো
pip install -r requirements.txt

# 3) Redis ইনস্টল করো ও চালাও (Celery broker হিসেবে লাগবে)
#    Ubuntu/Debian:  sudo apt install redis-server && redis-server
#    Mac (brew):     brew install redis && brew services start redis
#    Windows:        https://github.com/microsoftarchive/redis/releases
#                     অথবা Docker: docker run -p 6379:6379 redis

# 4) ডাটাবেস বানাও
python manage.py migrate

# (ঐচ্ছিক) অ্যাডমিন ইউজার বানাও — /admin/ থেকে সব লিড দেখতে পারবে
python manage.py createsuperuser
```

## প্রতিবার রান করতে ২টা টার্মিনাল লাগবে

**Terminal 1 — Django সার্ভার:**
```bash
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 — Celery worker (background এ scraping/validation চালাবে):**
```bash
source venv/bin/activate
celery -A leadfinder worker --loglevel=info
```

এখন ব্রাউজারে যাও: **http://127.0.0.1:8000/**

একটা টপিক লিখে সাবমিট করো (যেমন: `furniture shop Chittagong`), পেজ অটো-রিফ্রেশ হতে
থাকবে যতক্ষণ না রেজাল্ট রেডি হয়। তারপর CSV এক্সপোর্ট করতে পারবে।

## প্রজেক্ট স্ট্রাকচার

```
leadfinder/
├── leadfinder/        → settings.py (এখানে LEADFINDER_MAX_RESULTS দিয়ে প্রতি
│                         সার্চে কয়টা সাইট চেক হবে সেটা বদলানো যায়), celery.py
├── leads/
│   ├── models.py       → SearchJob, Lead
│   ├── forms.py        → টপিক ইনপুট ফর্ম
│   ├── tasks.py         → মূল লজিক: সার্চ → স্ক্র্যাপ → এক্সট্র্যাক্ট → ভ্যালিডেট
│   ├── views.py         → ফর্ম পেজ, জব ডিটেইল, CSV এক্সপোর্ট
│   └── templates/
├── requirements.txt
└── manage.py
```

## পরে যা আপগ্রেড করা যায় (দরকার হলে)

- **সার্চ স্টেবিলিটি:** DuckDuckGo স্ক্র্যাপিং রেট-লিমিট/ব্লকের সমস্যা করলে Google
  Programmable Search API (দিনে ১০০ কোয়েরি ফ্রি) বা SerpAPI-তে সুইচ করা যায় —
  শুধু `leads/tasks.py`-র `search_duckduckgo()` ফাংশন বদলালেই হবে।
- **ইমেইল ভ্যালিডেশন একুরেসি:** Hunter.io / ZeroBounce-এর মতো পেইড সার্ভিস যোগ করলে
  "mailbox আসলেই অ্যাক্টিভ কিনা" পর্যন্ত চেক করা যায় (এখন শুধু MX record চেক হয়)।
- **প্রোডাকশন ডিপ্লয়:** SQLite-এর বদলে PostgreSQL, আর `DEBUG = False` + proper
  `ALLOWED_HOSTS` সেট করতে হবে।
