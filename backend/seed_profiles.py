import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
import pathlib

# Load environment variables
current_dir = pathlib.Path(__file__).parent.resolve()
load_dotenv(current_dir / ".env")

# Connect to MongoDB
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["findr"]
users_collection = db.users

# Sample data
sample_profiles = [
    {
        "email": "sarah.code@example.com",
        "password": "password123",
        "name": "Sarah Chen",
        "skills": ["Python", "React", "Machine Learning", "TensorFlow"],
        "experience": [
            "ML Engineer at Tech Corp",
            "Research Assistant at University AI Lab",
            "Published paper on Neural Networks"
        ],
        "tags": ["AI/ML", "Full Stack", "Research", "Deep Learning"],
        "background": "Computer Science graduate with focus on AI",
        "school": "Stanford University",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "mike.dev@example.com",
        "password": "password123",
        "name": "Mike Rodriguez",
        "skills": ["JavaScript", "Node.js", "AWS", "MongoDB"],
        "experience": [
            "Full Stack Developer at StartupX",
            "Software Engineer Intern at Google",
            "Created popular npm package"
        ],
        "tags": ["Backend", "Cloud", "Open Source", "Startups"],
        "background": "Self-taught programmer with 5 years experience",
        "school": "Boot Camp Graduate",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "emily.ui@example.com",
        "password": "password123",
        "name": "Emily Taylor",
        "skills": ["UI/UX", "Figma", "HTML/CSS", "React"],
        "experience": [
            "UI Designer at Design Studio",
            "Freelance Web Designer",
            "Created viral mobile app interface"
        ],
        "tags": ["Design", "Frontend", "Mobile", "Creative"],
        "background": "Design school graduate with coding skills",
        "school": "Rhode Island School of Design",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "alex.data@example.com",
        "password": "password123",
        "name": "Alex Kim",
        "skills": ["SQL", "Python", "Tableau", "R"],
        "experience": [
            "Data Analyst at Finance Corp",
            "Business Intelligence Developer",
            "Created predictive models for retail"
        ],
        "tags": ["Data Science", "Analytics", "Finance", "Visualization"],
        "background": "Economics major with strong technical skills",
        "school": "UC Berkeley",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "jordan.security@example.com",
        "password": "password123",
        "name": "Jordan Patel",
        "skills": ["Cybersecurity", "Python", "Network Security", "Ethical Hacking"],
        "experience": [
            "Security Engineer at Bank",
            "Penetration Tester",
            "Bug bounty hunter"
        ],
        "tags": ["Security", "Privacy", "Blockchain", "Cryptography"],
        "background": "Cybersecurity specialist with CISSP certification",
        "school": "Georgia Tech",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "rachel.mobile@example.com",
        "password": "password123",
        "name": "Rachel Wong",
        "skills": ["Swift", "Kotlin", "React Native", "Firebase"],
        "experience": [
            "iOS Developer at Mobile Studio",
            "Android Developer",
            "Published multiple apps"
        ],
        "tags": ["Mobile", "iOS", "Android", "Cross-platform"],
        "background": "Mobile development expert",
        "school": "University of Washington",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "david.game@example.com",
        "password": "password123",
        "name": "David Martinez",
        "skills": ["Unity", "C#", "3D Modeling", "Game Design"],
        "experience": [
            "Game Developer at Gaming Studio",
            "Indie Game Creator",
            "Won Game Jam competition"
        ],
        "tags": ["Gaming", "VR/AR", "Unity", "Game Design"],
        "background": "Game development enthusiast",
        "school": "DigiPen Institute",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "lisa.cloud@example.com",
        "password": "password123",
        "name": "Lisa Johnson",
        "skills": ["AWS", "Docker", "Kubernetes", "Terraform"],
        "experience": [
            "DevOps Engineer at Cloud Corp",
            "System Administrator",
            "Cloud Architecture Consultant"
        ],
        "tags": ["DevOps", "Cloud", "Infrastructure", "Automation"],
        "background": "Cloud infrastructure specialist",
        "school": "MIT",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "kevin.blockchain@example.com",
        "password": "password123",
        "name": "Kevin Zhang",
        "skills": ["Solidity", "Web3.js", "Smart Contracts", "DeFi"],
        "experience": [
            "Blockchain Developer at Crypto Startup",
            "Smart Contract Auditor",
            "Created DeFi protocol"
        ],
        "tags": ["Blockchain", "DeFi", "Web3", "Crypto"],
        "background": "Blockchain technology expert",
        "school": "Cornell University",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "nina.product@example.com",
        "password": "password123",
        "name": "Nina Brown",
        "skills": ["Product Management", "Agile", "Data Analysis", "UX Research"],
        "experience": [
            "Product Manager at Tech Company",
            "Business Analyst",
            "Led product launches"
        ],
        "tags": ["Product", "Strategy", "Leadership", "Agile"],
        "background": "Product manager with technical background",
        "school": "Harvard Business School",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "tom.embedded@example.com",
        "password": "password123",
        "name": "Tom Wilson",
        "skills": ["C++", "Arduino", "IoT", "Embedded Systems"],
        "experience": [
            "Embedded Systems Engineer",
            "Hardware Developer",
            "IoT Project Lead"
        ],
        "tags": ["IoT", "Hardware", "Robotics", "Embedded"],
        "background": "Electrical engineering background",
        "school": "Caltech",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "maya.ai@example.com",
        "password": "password123",
        "name": "Maya Gupta",
        "skills": ["PyTorch", "NLP", "Computer Vision", "Deep Learning"],
        "experience": [
            "AI Researcher at Tech Lab",
            "Machine Learning Engineer",
            "Published AI papers"
        ],
        "tags": ["AI", "Research", "Deep Learning", "Innovation"],
        "background": "PhD in Machine Learning",
        "school": "Carnegie Mellon University",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "chris.testing@example.com",
        "password": "password123",
        "name": "Chris Lee",
        "skills": ["Test Automation", "Selenium", "Jenkins", "QA"],
        "experience": [
            "QA Lead at Software Corp",
            "Test Automation Engineer",
            "Quality Assurance Manager"
        ],
        "tags": ["Testing", "QA", "Automation", "CI/CD"],
        "background": "Quality assurance professional",
        "school": "University of Michigan",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "anna.frontend@example.com",
        "password": "password123",
        "name": "Anna Kowalski",
        "skills": ["Vue.js", "TypeScript", "GraphQL", "Sass"],
        "experience": [
            "Frontend Developer at Web Agency",
            "UI Engineer",
            "Created component library"
        ],
        "tags": ["Frontend", "UI", "Design Systems", "Web"],
        "background": "Frontend development specialist",
        "school": "NYU",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "james.backend@example.com",
        "password": "password123",
        "name": "James Anderson",
        "skills": ["Java", "Spring Boot", "Microservices", "Kafka"],
        "experience": [
            "Backend Engineer at Enterprise Corp",
            "Java Developer",
            "System Architect"
        ],
        "tags": ["Backend", "Java", "Architecture", "Enterprise"],
        "background": "Enterprise software developer",
        "school": "University of Illinois",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "sophia.ar@example.com",
        "password": "password123",
        "name": "Sophia Garcia",
        "skills": ["AR/VR", "Unity", "3D Design", "Motion Tracking"],
        "experience": [
            "AR Developer at Tech Studio",
            "VR Experience Designer",
            "Created AR mobile game"
        ],
        "tags": ["AR", "VR", "Gaming", "Interactive"],
        "background": "AR/VR development specialist",
        "school": "USC",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "ryan.data@example.com",
        "password": "password123",
        "name": "Ryan Murphy",
        "skills": ["Big Data", "Hadoop", "Spark", "Data Engineering"],
        "experience": [
            "Data Engineer at Big Tech",
            "Big Data Architect",
            "Built data pipelines"
        ],
        "tags": ["Big Data", "Data Engineering", "Analytics", "Cloud"],
        "background": "Data engineering expert",
        "school": "University of Texas",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "olivia.design@example.com",
        "password": "password123",
        "name": "Olivia Thompson",
        "skills": ["UI Design", "Adobe XD", "Sketch", "Design Systems"],
        "experience": [
            "Product Designer at Design Firm",
            "UX Researcher",
            "Design System Lead"
        ],
        "tags": ["Design", "UX", "Research", "Systems"],
        "background": "Product design specialist",
        "school": "Parsons School of Design",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "daniel.ml@example.com",
        "password": "password123",
        "name": "Daniel Kim",
        "skills": ["Machine Learning", "Data Science", "Python", "Scikit-learn"],
        "experience": [
            "ML Engineer at AI Startup",
            "Data Scientist",
            "Research Assistant"
        ],
        "tags": ["ML", "AI", "Research", "Analytics"],
        "background": "Machine learning engineer",
        "school": "UCLA",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    },
    {
        "email": "emma.security@example.com",
        "password": "password123",
        "name": "Emma Davis",
        "skills": ["Network Security", "Penetration Testing", "Security Auditing", "CISSP"],
        "experience": [
            "Security Consultant",
            "Network Security Engineer",
            "Security Analyst"
        ],
        "tags": ["Security", "Networks", "Compliance", "Risk"],
        "background": "Information security professional",
        "school": "Rochester Institute of Technology",
        "profile_completed": True,
        "created_at": datetime.utcnow()
    }
]

def seed_database():
    try:
        # Clear existing profiles
        users_collection.delete_many({})
        
        # Insert new profiles
        result = users_collection.insert_many(sample_profiles)
        print(f"✅ Successfully added {len(result.inserted_ids)} sample profiles to the database")
        
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")

if __name__ == "__main__":
    seed_database() 