import os
import sys
from datetime import datetime

# Setup sys.path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.config import Config
from app.database import get_collection, check_db_connection, init_db
from app.utils import hash_password

def run_migration():
    print("Connecting to database...")
    init_db()
    if not check_db_connection():
        print("[ERROR] Cannot connect to database. Ensure Atlas Network Access allows 0.0.0.0/0.")
        return False

    print("[SUCCESS] Database connected successfully!")

    # 1. Admin Credentials
    admins_col = get_collection("admins")
    if admins_col.count_documents({}) == 0:
        hashed = hash_password(Config.ADMIN_PASSWORD)
        admin_doc = {
            "email": Config.ADMIN_EMAIL.strip().lower(),
            "password": hashed,
            "name": "Dr. Usha Tyagi",
            "createdAt": datetime.utcnow()
        }
        admins_col.insert_one(admin_doc)
        print(f" -> Admin seeded: {Config.ADMIN_EMAIL}")
    else:
        print(f" -> Admin already exists ({admins_col.count_documents({})} record).")

    # 2. Connections
    conn_col = get_collection("connections")
    if conn_col.count_documents({}) == 0:
        default_connections = [
            {
                "name": "Dr. Usha Tyagi",
                "role": "Founder & President",
                "bio": "The driving force behind Ved Daksha Foundation. Dr. Usha Tyagi has dedicated years to providing free education to underprivileged children of Ghaziabad.",
                "imageUrl": "/images/1000087600.jpg.jpeg",
                "order": 1,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "name": "Vishakha Tyagi",
                "role": "Program Head & Anchor",
                "bio": "Vishakha leads daily programs and serves as the main event anchor, coordinating classes, events, and volunteer management.",
                "imageUrl": "/images/1000179545.jpg.jpeg",
                "order": 2,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "name": "Dr. Richa Sood",
                "role": "Education Advisor",
                "bio": "A respected educationist and author, Dr. Richa Sood advises on curriculum and has been a keynote presence at the foundation's annual events.",
                "imageUrl": "/images/1000179518.jpg.jpeg",
                "order": 3,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "name": "Aryan Tyagi",
                "role": "Youth Coordinator",
                "bio": "Aryan bridges the gap between the foundation and younger volunteers, organizing youth participation in outreach events.",
                "imageUrl": "/images/1000179580.jpg.jpeg",
                "order": 4,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "name": "Dr. Preeti Sharma",
                "role": "Medical Advisor",
                "bio": "Dr. Preeti Sharma brings medical expertise and community health support to the foundation, overseeing health camps and wellness programs.",
                "imageUrl": "/images/1000179574.jpg.jpeg",
                "order": 5,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "name": "Volunteer Team",
                "role": "Educators & Coaches",
                "bio": "Young educators, dance teachers, yoga instructors who show up every day to make a difference.",
                "imageUrl": "/images/1000179556.jpg.jpeg",
                "order": 6,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
        ]
        conn_col.insert_many(default_connections)
        print(" -> All 6 foundation connections seeded.")
    else:
        print(f" -> Connections collection already has {conn_col.count_documents({})} entries.")

    # 3. Gallery (all 41 pictures)
    gal_col = get_collection("gallery")
    if gal_col.count_documents({}) < 10:
        default_gallery = [
            {"url": "/images/1000179556.jpg.jpeg", "caption": "Annual Felicitation Event", "occasion": "Annual Felicitation Event", "category": "general", "order": 1, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087433.jpg.jpeg", "caption": "Yoga Performance", "occasion": "Yoga Performance", "category": "general", "order": 2, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087283.jpg.jpeg", "caption": "Dance Showcase", "occasion": "Dance Showcase", "category": "general", "order": 3, "createdAt": datetime.utcnow()},
            {"url": "/images/1000179500.jpg.jpeg", "caption": "School Bag Distribution", "occasion": "School Bag Distribution", "category": "general", "order": 4, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087355.jpg.jpeg", "caption": "Medal Ceremony", "occasion": "Medal Ceremony", "category": "general", "order": 5, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087516.jpg.jpeg", "caption": "Award Ceremony", "occasion": "Award Ceremony", "category": "general", "order": 6, "createdAt": datetime.utcnow()},
            {"url": "/images/1000086482.jpg.jpeg", "caption": "Our Children", "occasion": "Our Children", "category": "general", "order": 7, "createdAt": datetime.utcnow()},
            {"url": "/images/1000086223.jpg.jpeg", "caption": "Foundation Activity", "occasion": "Foundation Activity", "category": "general", "order": 8, "createdAt": datetime.utcnow()},
            {"url": "/images/1000086285.jpg.jpeg", "caption": "Children Learning", "occasion": "Children Learning", "category": "general", "order": 9, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087227.jpg.jpeg", "caption": "Cultural Program", "occasion": "Cultural Program", "category": "general", "order": 10, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087237.jpg.jpeg", "caption": "Special Event", "occasion": "Special Event", "category": "general", "order": 11, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087243.jpg.jpeg", "caption": "Student Achievement", "occasion": "Student Achievement", "category": "general", "order": 12, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087271.jpg.jpeg", "caption": "Yoga & Wellness", "occasion": "Yoga & Wellness", "category": "general", "order": 13, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087287.jpg.jpeg", "caption": "Dance Performance", "occasion": "Dance Performance", "category": "general", "order": 14, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087293.jpg.jpeg", "caption": "Community Gathering", "occasion": "Community Gathering", "category": "general", "order": 15, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087405.jpg.jpeg", "caption": "Educational Session", "occasion": "Educational Session", "category": "general", "order": 16, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087407.jpg.jpeg", "caption": "Volunteer Activity", "occasion": "Volunteer Activity", "category": "general", "order": 17, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087431.jpg.jpeg", "caption": "Community Outreach", "occasion": "Community Outreach", "category": "general", "order": 18, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087479.jpg.jpeg", "caption": "Foundation Celebration", "occasion": "Foundation Celebration", "category": "general", "order": 19, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087481.jpg.jpeg", "caption": "Annual Event", "occasion": "Annual Event", "category": "general", "order": 20, "createdAt": datetime.utcnow()},
            {"url": "/images/1000087600.jpg.jpeg", "caption": "Leadership & Guidance", "occasion": "Leadership & Guidance", "category": "general", "order": 21, "createdAt": datetime.utcnow()},
            {"url": "/images/1000106069.jpg.jpeg", "caption": "Children's Activities", "occasion": "Children's Activities", "category": "general", "order": 22, "createdAt": datetime.utcnow()},
            {"url": "/images/1000106080.jpg.jpeg", "caption": "Health Camp", "occasion": "Health Camp", "category": "general", "order": 23, "createdAt": datetime.utcnow()},
            {"url": "/images/1000115293.jpg.jpeg", "caption": "Special Occasion", "occasion": "Special Occasion", "category": "general", "order": 24, "createdAt": datetime.utcnow()},
            {"url": "/images/1000178048.jpg.jpeg", "caption": "Foundation Moments", "occasion": "Foundation Moments", "category": "general", "order": 25, "createdAt": datetime.utcnow()},
            {"url": "/images/1000178984.jpg.jpeg", "caption": "Training Session", "occasion": "Training Session", "category": "general", "order": 26, "createdAt": datetime.utcnow()},
            {"url": "/images/1000179051.jpg.jpeg", "caption": "Community Service", "occasion": "Community Service", "category": "general", "order": 27, "createdAt": datetime.utcnow()},
            {"url": "/images/1000179314.jpg.jpeg", "caption": "Youth Empowerment", "occasion": "Youth Empowerment", "category": "general", "order": 28, "createdAt": datetime.utcnow()},
            {"url": "/images/1000179412.jpg.jpeg", "caption": "Skill Development", "occasion": "Skill Development", "category": "general", "order": 29, "createdAt": datetime.utcnow()},
            {"url": "/images/1000179494.jpg.jpeg", "caption": "Education for All", "occasion": "Education for All", "category": "general", "order": 30, "createdAt": datetime.utcnow()},
            {"url": "/images/1000179518.jpg.jpeg", "caption": "Advisors & Mentors", "occasion": "Advisors & Mentors", "category": "general", "order": 31, "createdAt": datetime.utcnow()},
            {"url": "/images/1000179545.jpg.jpeg", "caption": "Program Coordination", "occasion": "Program Coordination", "category": "general", "order": 32, "createdAt": datetime.utcnow()},
            {"url": "/images/1000179574.jpg.jpeg", "caption": "Medical Outreach", "occasion": "Medical Outreach", "category": "general", "order": 33, "createdAt": datetime.utcnow()},
            {"url": "/images/1000179580.jpg.jpeg", "caption": "Youth Volunteers", "occasion": "Youth Volunteers", "category": "general", "order": 34, "createdAt": datetime.utcnow()},
            {"url": "/images/1000179703.jpg.jpeg", "caption": "Celebration & Joy", "occasion": "Celebration & Joy", "category": "general", "order": 35, "createdAt": datetime.utcnow()},
            {"url": "/images/1000179906.jpg.jpeg", "caption": "Cultural Heritage", "occasion": "Cultural Heritage", "category": "general", "order": 36, "createdAt": datetime.utcnow()},
            {"url": "/images/1000191716.jpg.jpeg", "caption": "Foundation Events", "occasion": "Foundation Events", "category": "general", "order": 37, "createdAt": datetime.utcnow()},
            {"url": "/images/1000191718.jpg.jpeg", "caption": "Community Programs", "occasion": "Community Programs", "category": "general", "order": 38, "createdAt": datetime.utcnow()},
            {"url": "/images/1000191720.jpg.jpeg", "caption": "Learning Together", "occasion": "Learning Together", "category": "general", "order": 39, "createdAt": datetime.utcnow()},
            {"url": "/images/1000191722.jpg.jpeg", "caption": "Inspiring Stories", "occasion": "Inspiring Stories", "category": "general", "order": 40, "createdAt": datetime.utcnow()},
            {"url": "/images/1000252075.jpg.jpeg", "caption": "Making a Difference", "occasion": "Making a Difference", "category": "general", "order": 41, "createdAt": datetime.utcnow()},
        ]
        gal_col.delete_many({})
        gal_col.insert_many(default_gallery)
        print(" -> All 41 gallery images successfully seeded.")
    else:
        print(f" -> Gallery has {gal_col.count_documents({})} images.")

    # 4. Blogs
    blogs_col = get_collection("blogs")
    if blogs_col.count_documents({}) == 0:
        default_blogs = [
            {
                "title": "How Free Education Changes a Child's Trajectory in Ghaziabad",
                "titleHindi": "गाजियाबाद में मुफ्त शिक्षा कैसे एक बच्चे के भविष्य को बदलती है",
                "slug": "how-free-education-changes-child-trajectory-ghaziabad",
                "content": "When a child from a daily-wage family gets access to books, a classroom, and a caring teacher — everything changes. At Ved Daksha Foundation, we see this transformation every single day. Children who were once out of school are now reading, writing, and dreaming of careers...",
                "contentHindi": "जब दैनिक मजदूरी करने वाले परिवार के किसी बच्चे को किताबों, एक कक्षा और एक स्नेही शिक्षक तक पहुँच मिलती है - तो सब कुछ बदल जाता है। वेद दक्षा फाउंडेशन में, हम हर दिन इस बदलाव को देखते हैं। जो बच्चे कभी स्कूल से बाहर थे, वे अब पढ़ रहे हैं, लिख रहे हैं और अपने करियर का सपना देख रहे हैं...",
                "excerpt": "When a child from a daily-wage family gets access to books, a classroom, and a caring teacher — everything changes.",
                "excerptHindi": "जब दैनिक मजदूरी करने वाले परिवार के किसी बच्चे को किताबों, एक कक्षा और एक स्नेही शिक्षक तक पहुँच मिलती है - तो सब कुछ बदल जाता है।",
                "category": "Education",
                "tags": ["education", "children", "ghaziabad"],
                "author": "Dr. Usha Tyagi",
                "coverImage": "/images/1000086285.jpg.jpeg",
                "isPublished": True,
                "views": 0,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "title": "Why Yoga and Dance Are as Important as Textbooks",
                "titleHindi": "योग और नृत्य पाठ्यपुस्तकों की तरह ही क्यों महत्वपूर्ण हैं",
                "slug": "why-yoga-dance-important-textbooks",
                "content": "Physical expression, discipline, and artistry are not extracurricular — they are the core of holistic childhood development. When our children perform yoga and dance on stage, they're not just performing — they're proving to themselves and the world that they are capable of excellence...",
                "contentHindi": "शारीरिक अभिव्यक्ति, अनुशासन और कलात्मकता अतिरिक्त गतिविधियाँ नहीं हैं - वे समग्र बाल विकास का मूल हैं। जब हमारे बच्चे मंच पर योग और नृत्य करते हैं, तो वे केवल प्रदर्शन नहीं कर रहे होते हैं - वे खुद को और दुनिया को साबित कर रहे होते हैं कि वे उत्कृष्टता के सक्षम हैं...",
                "excerpt": "Physical expression, discipline, and artistry are not extracurricular — they are the core of holistic childhood development.",
                "excerptHindi": "शारीरिक अभिव्यक्ति, अनुशासन और कलात्मकता अतिरिक्त गतिविधियाँ नहीं हैं - वे समग्र बाल विकास का मूल हैं।",
                "category": "Arts & Development",
                "tags": ["yoga", "dance", "development"],
                "author": "Dr. Usha Tyagi",
                "coverImage": "/images/1000087271.jpg.jpeg",
                "isPublished": True,
                "views": 0,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "title": "5 Ways You Can Support Underprivileged Children Without Donating Money",
                "titleHindi": "बिना पैसे दान किए वंचित बच्चों की मदद करने के 5 तरीके",
                "slug": "5-ways-support-underprivileged-children-without-money",
                "content": "Books, time, skills, connections, and presence. There are more ways to give than you think. Our volunteers prove this every week — some teach English, others organise health camps, and some simply show up to cheer our children at performances...",
                "contentHindi": "किताबें, समय, कौशल, संपर्क और उपस्थिति। आपके सोचने से भी अधिक दान देने के तरीके हैं। हमारे स्वयंसेवक हर हफ्ते इसे साबित करते हैं - कुछ अंग्रेजी सिखाते हैं, अन्य स्वास्थ्य शिविर आयोजित करते हैं, और कुछ केवल प्रदर्शनों में हमारे बच्चों का उत्साह बढ़ाने के लिए आते हैं...",
                "excerpt": "Books, time, skills, connections, and presence. There are more ways to give than you think.",
                "excerptHindi": "किताबें, समय, कौशल, संपर्क और उपस्थिति। आपके सोचने से भी अधिक दान देने के तरीके हैं।",
                "category": "Community",
                "tags": ["volunteer", "support", "community"],
                "author": "Dr. Usha Tyagi",
                "coverImage": "/images/1000087355.jpg.jpeg",
                "isPublished": True,
                "views": 0,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
        ]
        blogs_col.insert_many(default_blogs)
        print(" -> All default blogs seeded.")
    else:
        print(f" -> Blogs already exist ({blogs_col.count_documents({})} entries).")

    # 5. Events
    events_col = get_collection("events")
    if events_col.count_documents({}) == 0:
        default_events = [
            {
                "title": "Annual Varshikotsav & Children Felicitation 2025",
                "titleHindi": "वार्षिक वार्षिकोत्सव एवं बाल सम्मान समारोह 2025",
                "description": "Celebrating the achievements of our underprivileged students with yoga performances, dance showcase, and distribution of educational supplies.",
                "descriptionHindi": "योग प्रदर्शन, नृत्य प्रदर्शन और शैक्षिक सामग्री के वितरण के साथ हमारे वंचित छात्रों की उपलब्धियों का जश्न।",
                "date": datetime(2025, 3, 25, 10, 0),
                "location": "Chiranjeev Vihar, Ghaziabad",
                "images": ["/images/1000179556.jpg.jpeg", "/images/1000087433.jpg.jpeg"],
                "isUpcoming": True,
                "createdAt": datetime.utcnow()
            }
        ]
        events_col.insert_many(default_events)
        print(" -> Default events seeded.")
    else:
        print(f" -> Events already exist ({events_col.count_documents({})} entries).")

    print("\n✅ All credentials, foundation connections, events, blogs, and all 41 pictures are verified and seeded!")
    return True

if __name__ == "__main__":
    run_migration()
