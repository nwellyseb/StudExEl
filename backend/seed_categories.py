from app import app
from extensions import db
from models.category import Category


categories = [

    # Academic Materials
    {
        "category_name": "Textbooks",
        "slug": "textbooks",
        "description": "College textbooks, reference books, and reading materials"
    },

    {
        "category_name": "Reviewers & Notes",
        "slug": "reviewers-notes",
        "description": "Review materials, lecture notes, and study guides"
    },

    {
        "category_name": "School Supplies",
        "slug": "school-supplies",
        "description": "Notebooks, pens, paper, folders, and supplies"
    },

    {
        "category_name": "Calculators",
        "slug": "calculators",
        "description": "Scientific, engineering, and graphing calculators"
    },

    {
        "category_name": "Laboratory Equipment",
        "slug": "laboratory-equipment",
        "description": "Lab coats, tools, and laboratory materials"
    },


    # Electronics
    {
        "category_name": "Laptops & Computers",
        "slug": "laptops-computers",
        "description": "Laptops, desktops, tablets, and computer accessories"
    },

    {
        "category_name": "Phones & Tablets",
        "slug": "phones-tablets",
        "description": "Mobile phones, tablets, and accessories"
    },

    {
        "category_name": "Computer Accessories",
        "slug": "computer-accessories",
        "description": "Keyboards, mice, chargers, and peripherals"
    },

    {
        "category_name": "Audio Devices",
        "slug": "audio-devices",
        "description": "Headphones, speakers, and microphones"
    },


    # Clothing
    {
        "category_name": "School Uniforms",
        "slug": "school-uniforms",
        "description": "School uniforms, PE uniforms, and organization shirts"
    },

    {
        "category_name": "Clothing & Shoes",
        "slug": "clothing-shoes",
        "description": "Casual clothing, shoes, and accessories"
    },

    {
        "category_name": "Bags & Backpacks",
        "slug": "bags-backpacks",
        "description": "School bags, backpacks, and luggage"
    },


    # Dorm & Living
    {
        "category_name": "Dorm Essentials",
        "slug": "dorm-essentials",
        "description": "Dorm items, organizers, and personal essentials"
    },

    {
        "category_name": "Furniture",
        "slug": "furniture",
        "description": "Tables, chairs, shelves, and storage"
    },

    {
        "category_name": "Appliances",
        "slug": "appliances",
        "description": "Small appliances for dorms and apartments"
    },


    # Transportation
    {
        "category_name": "Bicycles",
        "slug": "bicycles",
        "description": "Bicycles and cycling accessories"
    },

    {
        "category_name": "Transportation Accessories",
        "slug": "transportation-accessories",
        "description": "Helmets, locks, and commuting equipment"
    },


    # Creative & Hobbies
    {
        "category_name": "Art Supplies",
        "slug": "art-supplies",
        "description": "Drawing, painting, and creative materials"
    },

    {
        "category_name": "Musical Instruments",
        "slug": "musical-instruments",
        "description": "Instruments and music accessories"
    },

    {
        "category_name": "Sports Equipment",
        "slug": "sports-equipment",
        "description": "Sports gear and fitness equipment"
    },


    # Services
    {
        "category_name": "Tutoring Services",
        "slug": "tutoring-services",
        "description": "Student tutoring and academic assistance"
    },

    {
        "category_name": "Freelance Services",
        "slug": "freelance-services",
        "description": "Design, editing, programming, and other services"
    },


    # Other
    {
        "category_name": "Food & Snacks",
        "slug": "food-snacks",
        "description": "Student-made food and snacks"
    },

    {
        "category_name": "Tickets & Events",
        "slug": "tickets-events",
        "description": "Event tickets and school activities"
    },

    {
        "category_name": "Others",
        "slug": "others",
        "description": "Anything else suitable for students"
    }

]


with app.app_context():

    for item in categories:

        existing = Category.query.filter_by(
            slug=item["slug"]
        ).first()


        if not existing:

            category = Category(
                category_name=item["category_name"],
                slug=item["slug"],
                description=item["description"]
            )

            db.session.add(category)


    db.session.commit()


print("Marketplace categories updated successfully!")