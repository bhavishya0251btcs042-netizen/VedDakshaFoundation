# 🌿 Ved Daksha Foundation — Complete Website

**वय राष्ट्रे जागृयाम** | Empowering Underprivileged Children, Ghaziabad

---

## 📁 Project Structure

```
ved_daksha/
├── index_v2.html          ← Main website (homepage)
├── blog.html              ← Blog listing page
├── admin/
│   └── index.html         ← Admin portal (login protected)
├── backend/
│   ├── server.js          ← Express server entry point
│   ├── .env               ← Environment variables (FILL THIS IN)
│   ├── models/index.js    ← MongoDB schemas
│   ├── routes/
│   │   ├── auth.js        ← Login / password change
│   │   ├── events.js      ← Events CRUD + image upload
│   │   ├── donations.js   ← Donations + email confirmation
│   │   ├── blog.js        ← Blog CRUD
│   │   ├── gallery.js     ← Gallery management
│   │   └── contact.js     ← Contact form messages
│   └── middleware/auth.js ← JWT authentication
└── images/                ← All NGO photos
```

---

## 🚀 Setup Instructions

### Step 1 — MongoDB Atlas (Free)
1. Go to https://cloud.mongodb.com and create a free account
2. Create a new cluster (free tier)
3. Click **Connect** → **Drivers** → copy the connection string
4. Replace `<username>` and `<password>` with your DB user credentials

### Step 2 — Configure Environment
Open `backend/.env` and fill in:
```env
MONGODB_URI=mongodb+srv://youruser:yourpass@cluster0.xxxxx.mongodb.net/veddaksha
JWT_SECRET=any_long_random_string_here_min_32_chars
ADMIN_EMAIL=your-admin-email@example.com
ADMIN_PASSWORD=YourSecurePassword123!
EMAIL_USER=veddakshafoundation22@gmail.com
EMAIL_PASS=your_gmail_app_password
```

**To get Gmail App Password:**
1. Go to Google Account → Security → 2-Step Verification (enable it)
2. Then Security → App passwords → Generate one for "Mail"
3. Paste the 16-character code as `EMAIL_PASS`

### Step 3 — Install & Run Backend
```bash
cd backend
npm install
node server.js
```
Server runs at: `http://localhost:5000`

### Step 4 — First-Time Admin Setup
After server starts, run this ONCE to create the admin account:
```bash
curl -X POST http://localhost:5000/api/auth/setup
```

### Step 5 — Open the Website
- **Main site:** Open `index_v2.html` in browser
- **Admin portal:** Open `admin/index.html` in browser
- **Blog:** Open `blog.html` in browser

---

## 🔐 Admin Portal Features

| Feature | Description |
|---------|-------------|
| **Dashboard** | Stats, countdown timer for next event, recent donations |
| **Events** | Add/edit/delete events with image upload, upcoming/past filter |
| **Gallery** | Upload and manage gallery images |
| **Blog** | Write and publish blog posts |
| **Donations** | View all donations, confirm/reject payment status |
| **Messages** | Read contact form submissions, mark as read |
| **Settings** | Change admin password |

---

## 🎨 Logo Design Prompt

Use this prompt with **Midjourney**, **Adobe Firefly**, **Ideogram**, or **Canva AI**:

```
Create a professional NGO logo for "VED DAKSHA FOUNDATION" with tagline 
"वय राष्ट्रे जागृयाम". The logo should feature two or three human figures 
with raised arms forming a protective circle, symbolizing education and 
community. Use deep forest green (#1B6B3A) as primary color with saffron 
orange (#E07B2A) as accent. Include a subtle lotus or book element. 
Clean vector style, suitable for print and digital. Modern but culturally 
rooted in Indian NGO aesthetic. White background. Include both English and 
Hindi text. Professional and trustworthy.
```

**Alternative prompt for Canva:**
```
NGO logo, two children reading books under a protective arch, 
deep green color #1B6B3A, Indian cultural style, "VED DAKSHA FOUNDATION" 
text, lotus symbol, clean modern vector design
```

---

## 📝 Blog Post Ideas (Pre-written topics)

1. **How Free Education Changes a Child's Trajectory in Ghaziabad**
2. **Why Yoga and Dance Are as Important as Textbooks**  
3. **5 Ways to Support Underprivileged Children Without Donating Money**
4. **From the Streets to the Stage: Stories of Our Students**
5. **What Volunteering at an NGO Taught Me About My Own Privilege**
6. **Dr. Usha Tyagi: The Woman Who Started a Revolution in Her Neighbourhood**
7. **The Role of Martial Arts in Girls' Safety and Confidence**
8. **How to Write a Will That Includes a Charitable Bequest**
9. **CSR and NGO Partnerships: A Guide for Ghaziabad Businesses**
10. **Republic Day at the Foundation: Teaching Patriotism Through Action**

---

## 🌐 Deployment (Free Hosting)

### Frontend (Netlify — Free)
1. Go to https://netlify.com
2. Drag and drop your `ved_daksha/` folder
3. Your site is live in seconds!
4. Set custom domain: `www.veddakshafoundation.org`

### Backend (Railway — Free tier)
1. Go to https://railway.app
2. Connect your GitHub repo
3. Add the backend folder as a service
4. Set all environment variables in Railway's dashboard
5. Your API will be at: `https://your-app.railway.app`

### Update API URL
After deployment, change `const API = 'http://localhost:5000/api'` in both 
`index_v2.html` and `admin/index.html` to your Railway URL.

---

## 📱 Social Media Handles
- **Facebook:** facebook.com/VedDakshaFoundation
- **Instagram:** @ved.dakshafoundation  
- **YouTube:** @veddakshafoundation22
- **WhatsApp:** 8700785399

## 📞 Contact
- Phone: 8700785399 | 8595656658
- Email: veddakshafoundation22@gmail.com
- Address: 7/56, Chiranjeev Vihar, Ghaziabad – 201002
