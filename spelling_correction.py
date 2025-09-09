from rapidfuzz import process, fuzz

# === Product List ===
grocery_products = {
    "Clothing & Accessories": [
        "Shirts", "T-Shirts", "Pants", "Jeans", "Jackets", "Sweaters",
        "Shalwar Kameez", "Saree", "Kurta", "Abaya", "Hijab",
        "Shoes", "Sandals", "Slippers", "Socks",
        "Caps", "Hats", "Scarves", "Gloves", "Belts",
        "Watches", "Sunglasses", "Handbags", "Wallets"
    ],
    "Food": [
        "Rice", "Wheat Flour (Atta)", "Maize", "Oats", "Barley",
        "Potatoes", "Onions", "Tomatoes", "Spinach", "Carrots", "Cabbage", "Cauliflower", "Peas", "Okra",
        "Apples", "Bananas", "Mangoes", "Oranges", "Grapes", "Papaya", "Guava", "Dates",
        "Chicken", "Mutton", "Beef", "Fish", "Eggs", "Pulses", "Lentils", "Chickpeas",
        "Milk", "Yogurt", "Cheese", "Butter", "Ghee", "Cream",
        "Chips", "Biscuits", "Chocolates", "Cakes", "Namkeen", "Noodles", "Instant Soup",
        "Honey", "Jam", "Pickles", "Dry Fruits", "Nuts", "Sugar", "Salt", "Spices"
    ],
    "Drinks": [
        "Water", "Tea", "Green Tea", "Herbal Tea", "Coffee",
        "Mango Juice", "Orange Juice", "Apple Juice", "Lemon Juice",
        "Coke", "Pepsi", "7Up", "Sprite",
        "Red Bull", "Sting", "Monster", "Mountain Dew",
        "Milkshake", "Smoothie", "Sharbat", "Rooh Afza"
    ],
    "Household Items": [
        "Beds", "Sofas", "Tables", "Chairs", "Cupboards", "Mattress", "Pillows", "Blankets", "Bedsheets",
        "Stove", "Fridge", "Microwave", "Blender", "Kettle", "Toaster", "Pressure Cooker",
        "Utensils", "Plates", "Glasses", "Spoons", "Knives", "Pans", "Cooking Pots", "Storage Containers",
        "Broom", "Mop", "Vacuum Cleaner", "Detergent", "Soap", "Sanitizer",
        "Shampoo", "Toothpaste", "Toothbrush", "Conditioner", "Towels", "Toilet Paper", "Tissue Paper",
        "Curtains", "Cushions", "Tablecloth"
    ],
    "Electronics & Gadgets": [
        "Smartphone", "Laptop", "Tablet", "Television", "LED Lights",
        "Refrigerator", "Washing Machine", "Camera", "Microwave Oven",
        "Headphones", "Speakers", "Smartwatch", "Fitness Band",
        "Charger", "Power Bank", "Extension Cables", "Fans", "Heater", "Air Conditioner", "Iron"
    ],
    "Transportation": [
        "Car", "Motorbike", "Bicycle", "Rickshaw", "Bus", "Train", "Metro", "Boat", "Airplane",
        "Petrol", "Diesel", "CNG", "Electric Charging", "Tyres", "Engine Oil"
    ],
    "Personal Care": [
        "Perfume", "Deodorant", "Cream", "Lotion", "Face Wash", "Body Wash",
        "Shaving Kit", "Razor", "Hair Oil", "Hair Dryer", "Comb", "Mirror",
        "Lipstick", "Foundation", "Kajal", "Nail Polish", "Sunscreen"
    ],
    "Health & Medicine": [
        "First Aid Kit", "Bandages", "Antiseptic", "Painkiller", "Cough Syrup",
        "Antibiotics", "Diabetes Medicine", "Hypertension Medicine",
        "Vitamins", "Supplements", "Mask", "Sanitizer", "Thermometer", "Blood Pressure Monitor"
    ],
    "Education & Office": [
        "Books", "Notebooks", "Pens", "Pencils", "Markers", "Eraser", "Sharpener",
        "Bag", "Files", "Calculator", "Whiteboard", "Markers",
        "Computer", "Printer", "Photocopier", "Stapler", "Paper Reams"
    ],
    "Entertainment": [
        "Toys", "Board Games", "Video Games", "Playing Cards",
        "Football", "Cricket Bat", "Tennis Racket", "Badminton Racket", "Gym Equipment",
        "Guitar", "Piano", "Drums", "TV", "Speakers"
    ],
    "Baby & Kids": [
        "Diapers", "Baby Lotion", "Baby Powder", "Baby Soap", "Baby Shampoo",
        "Feeder Bottles", "Baby Wipes", "Baby Food", "Pacifier", "Rattle Toys"
    ],
    "Miscellaneous": [
        "Ring", "Bracelet", "Necklace", "Earrings", "Watch Battery",
        "Watering Can", "Shovel", "Seeds", "Flower Pots", "Fertilizer",
        "Dog Food", "Cat Food", "Bird Food", "Cage", "Fish Tank",
        "Batteries", "Umbrella", "Wall Clock", "Torch"
    ]
}

# === Flatten all products manually ===
all_products = []
for category, items in grocery_products.items():
    for item in items:
        all_products.append(item)

# === Suggestion function ===
def suggest_alternatives(word: str, limit: int = 5):
    related = process.extract(word, all_products, limit=limit, scorer=fuzz.token_sort_ratio)
    suggestions = []
    for r in related:
        if r[1] > 40:   # only add if similarity is good
            suggestions.append(r[0])
    return suggestions

# === Spelling correction function ===
def correct_spelling(word: str):
    best_match, score, _ = process.extractOne(word, all_products, scorer=fuzz.token_sort_ratio)

    if score >= 75:   # High confidence
        return {"corrected": best_match, "alternatives": []}

    elif 55 <= score < 75:   # Medium confidence
        suggestions = process.extract(word, all_products, limit=3, scorer=fuzz.token_sort_ratio)
        alternatives = []
        for s in suggestions:
            if s[0] != best_match:
                alternatives.append(s[0])
        return {"corrected": best_match, "alternatives": alternatives}

    else:   # Low confidence
        return {"corrected": None, "alternatives": suggest_alternatives(word)}
