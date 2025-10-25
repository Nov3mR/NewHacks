#!/usr/bin/env python3
"""
Setup script to create sample travel data files
Run this to generate example documents in the data/ folder
"""

import os

# Create data directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Sample travel documents
SAMPLE_DOCUMENTS = {
    "japan-activities.txt": """Japan Travel Guide - Activities and Attractions

TOKYO
Must-Visit Attractions:
- Senso-ji Temple: Tokyo's oldest temple in Asakusa. Best visited early morning to avoid crowds. Free entry.
- Tsukiji Outer Market: Famous for fresh sushi and street food. Open from 5 AM. Budget: $20-40 per person.
- Shibuya Crossing: World's busiest pedestrian crossing. Visit at night for the full neon experience.
- TeamLab Borderless: Digital art museum in Odaiba. Tickets: $30. Book in advance.
- Tokyo Skytree: 634m tower with observation decks. Tickets: $20-30. Best at sunset.

Food Experiences:
- Ramen tasting tour in Shinjuku: Try different regional styles. Budget: $30-50.
- Sushi making class: Learn from a master chef. 3 hours, $80-100.
- Izakaya hopping in Shibuya: Traditional Japanese pub crawl. Budget: $40-60.

KYOTO
Cultural Highlights:
- Fushimi Inari Shrine: Famous for thousands of red torii gates. Free entry, allow 2-3 hours.
- Kinkaku-ji (Golden Pavilion): Stunning gold-covered temple. Entry: $5. Best in morning light.
- Arashiyama Bamboo Grove: Walk through towering bamboo forest. Free, best early morning.
- Gion District: Traditional geisha district. Free to walk around, best at dusk.

Seasonal Activities:
- Cherry blossom viewing (March-April): Maruyama Park and Philosopher's Path
- Fall foliage (November): Tofuku-ji Temple and Eikando Temple
- Summer festivals: Gion Matsuri in July

OSAKA
Food Paradise:
- Dotonbori: Neon-lit food street. Try takoyaki and okonomiyaki. Budget: $20-30.
- Kuromon Market: "Osaka's Kitchen" with fresh seafood and street food.
- Kushikatsu alley: Deep-fried skewers on sticks. Budget: $25-40.

Entertainment:
- Osaka Castle: Historic castle with museum. Entry: $8. Allow 2 hours.
- Universal Studios Japan: Theme park with Harry Potter area. Tickets: $70-80.
- Spa World: Multi-story onsen theme park. Entry: $15.

MOUNT FUJI & HAKONE
Nature Activities:
- Mount Fuji climbing (July-September): 5-7 hour ascent. Guided tours: $100-150.
- Hakone Open-Air Museum: Sculpture garden with mountain views. Entry: $15.
- Lake Ashi Cruise: Scenic boat ride with Fuji views. Tickets: $10-15.
- Owakudani Valley: Active volcanic area with black eggs. Ropeway: $8.

Best Times to Visit:
- Tokyo: Year-round, cherry blossoms in late March-April
- Kyoto: March-May and October-November for best weather
- Mount Fuji: Climbing season July-September
- Winter sports: December-March in Hokkaido and Nagano

Transportation Tips:
- JR Pass: 7-day unlimited train pass ($280) worth it if traveling between cities
- IC Card (Suica/Pasmo): $5 deposit, works on all trains and buses
- Pocket WiFi rental: $8-10 per day
""",

    "europe-destinations.txt": """European Travel Guide - Top Destinations

ITALY
Rome:
Perfect for history lovers and food enthusiasts. Budget: $100-150/day moderate, $200+ luxury.
Highlights: Colosseum, Vatican City, Roman Forum, Trevi Fountain, Trastevere neighborhood
Best time: April-May, September-October. Summer very crowded and hot.
Insider tip: Book Colosseum and Vatican tickets online weeks in advance to skip massive lines.

Florence:
Renaissance art capital. Budget: $80-120/day.
Must-see: Uffizi Gallery, Duomo, Michelangelo's David, Ponte Vecchio
Food: Try bistecca alla fiorentina (Florentine steak) and gelato from local shops
Best for: Art lovers, architecture enthusiasts, wine tasting (nearby Tuscany)

Venice:
Unique floating city. Budget: $120-180/day (pricier than other Italian cities).
Experiences: Gondola ride, St. Mark's Basilica, Doge's Palace, Rialto Market
Tips: Visit in fall or winter to avoid massive crowds. Stay on main island for full experience.

FRANCE
Paris:
Cultural hub perfect for first-time Europe visitors. Budget: $120-200/day.
Icons: Eiffel Tower, Louvre, Notre-Dame, Champs-Élysées, Montmartre
Food scene: Café culture, patisseries, wine bars, Michelin-star restaurants
Best season: Spring (April-June) for perfect weather and blooming gardens.

French Riviera (Nice, Cannes, Monaco):
Beach destination with glamour. Budget: $150-250/day.
Activities: Beach clubs, yacht watching, Promenade des Anglais, perfume workshops
Best for: Luxury travelers, beach lovers, summer vacation (June-September)

SPAIN
Barcelona:
Creative, vibrant city. Budget: $90-140/day.
Gaudí masterpieces: Sagrada Familia, Park Güell, Casa Batlló
Culture: Beach life, tapas bars, flamenco shows, Las Ramblas
Best for: Architecture fans, beach + city combo, food lovers

Madrid:
Spain's cultural heart. Budget: $80-130/day.
Museums: Prado, Reina Sofia (Guernica), Thyssen-Bornemisza
Lifestyle: Late dinners (10 PM+), nightlife until dawn, tapas hopping
Perfect for: Art enthusiasts, night owls, authentic Spanish culture

GREECE
Athens:
Ancient history comes alive. Budget: $70-110/day.
Must-visit: Acropolis, Parthenon, Ancient Agora, Plaka neighborhood
Food: Greek tavernas, souvlaki, moussaka, fresh seafood
Combine with: Island hopping to Santorini or Mykonos

Greek Islands (Santorini, Mykonos, Crete):
Picture-perfect paradise. Budget: $100-200/day depending on island.
Santorini: Sunsets in Oia, white-washed buildings, wine tasting, volcanic beaches
Mykonos: Beach parties, windmills, Little Venice, cosmopolitan atmosphere
Crete: Largest island, diverse: beaches, mountains, Minoan palaces, traditional villages
Best time: May-June or September-October (July-August very crowded and expensive)

UNITED KINGDOM
London:
Global city mixing history and modernity. Budget: $130-200/day.
Free attractions: British Museum, National Gallery, changing of guard, parks
Paid highlights: Tower of London, Westminster Abbey, London Eye, theatre shows
Food: Traditional pubs, afternoon tea, international cuisine, street markets
Best for: Museum lovers, theatre fans, diverse experiences

Edinburgh:
Historic Scottish capital. Budget: $90-140/day.
Highlights: Edinburgh Castle, Royal Mile, Arthur's Seat hike, whisky tasting
Best time: August for Edinburgh Festival Fringe (book accommodation early!)
Perfect for: History buffs, Harry Potter fans, nature + city combo

PORTUGAL
Lisbon:
Trendy European capital on budget. Budget: $70-110/day.
Experiences: Tram 28 ride, Belém Tower, Jerónimos Monastery, Fado music
Food: Pastéis de nata, seafood, port wine
Best for: Budget travelers, foodies, great weather year-round

Porto:
Charming wine city. Budget: $60-100/day.
Activities: Port wine cellars, Douro Valley tour, Livraria Lello bookshop, riverside walks
Perfect for: Wine lovers, couples, relaxed atmosphere

NETHERLANDS
Amsterdam:
Bike-friendly canal city. Budget: $100-160/day.
Must-do: Canal cruise, Anne Frank House, Van Gogh Museum, Rijksmuseum, cycling everywhere
Scene: Coffee shops, brown cafés, tulip fields (April-May), liberal atmosphere
Best for: Cyclists, art lovers, open-minded travelers

GERMANY
Berlin:
Historical and alternative city. Budget: $80-130/day.
History: Berlin Wall, Brandenburg Gate, Holocaust Memorial, Checkpoint Charlie
Culture: Street art, nightlife scene, museums, currywurst
Best for: History enthusiasts, party people, alternative culture

Munich:
Bavarian traditions meet modernity. Budget: $90-150/day.
Highlights: Marienplatz, beer gardens, Neuschwanstein Castle day trip
Oktoberfest: September-October, book accommodation 6+ months ahead
Perfect for: Beer lovers, traditional German experience

Travel Tips:
- Schengen Visa: Covers most European countries, allows 90 days in 180-day period
- Rail passes: Eurail pass good value if visiting multiple countries
- Budget airlines: Ryanair, EasyJet for cheap inter-city flights
- Accommodation: Mix of hotels, hostels, Airbnb depending on budget
- Best time: Shoulder seasons (April-May, September-October) for fewer crowds and good weather
""",

    "southeast-asia-guide.txt": """Southeast Asia Travel Guide

THAILAND
Bangkok:
Vibrant capital city. Budget: $30-50/day.
Must-see: Grand Palace, Wat Pho (Reclining Buddha), Wat Arun, floating markets, Khao San Road
Food: Street food paradise. Try pad thai, som tam, mango sticky rice
Nightlife: Rooftop bars, night markets, Soi Cowboy
Best for: First-time Asia travelers, foodies, budget travelers

Chiang Mai:
Northern cultural hub. Budget: $25-40/day.
Activities: Temple hopping (300+ temples), elephant sanctuaries, Thai cooking classes
Nature: Doi Suthep mountain, waterfalls, jungle trekking
Perfect for: Digital nomads, nature lovers, culture seekers

Phuket & Islands:
Beach paradise. Budget: $40-80/day.
Islands: Phi Phi Islands, James Bond Island, Similan Islands
Activities: Snorkeling, diving, island hopping, beach parties
Best time: November-April (dry season)

VIETNAM
Hanoi:
Chaotic but charming capital. Budget: $30-45/day.
Highlights: Old Quarter, Hoan Kiem Lake, street food tours, cyclo rides
Food: Pho, bun cha, egg coffee, banh mi
Day trips: Ha Long Bay cruise (UNESCO site)

Ho Chi Minh City (Saigon):
Modern southern metropolis. Budget: $30-50/day.
History: War Remnants Museum, Cu Chi Tunnels
Food: Street food in District 1, Ben Thanh Market
Nightlife: Rooftop bars, Bui Vien backpacker street

Hoi An:
Ancient town UNESCO site. Budget: $25-40/day.
Attractions: Japanese Bridge, lantern-lit old town, tailors (custom clothes)
Beach: An Bang Beach nearby
Best for: Photography, relaxation, shopping

CAMBODIA
Siem Reap (Angkor Wat):
Temple complex wonder. Budget: $30-45/day.
Temples: Angkor Wat sunrise, Bayon (faces), Ta Prohm (Tomb Raider temple)
Passes: 1-day ($37), 3-day ($62). Hire tuk-tuk driver for temples
Best time: November-February (cool and dry)

Phnom Penh:
Capital with sobering history. Budget: $25-40/day.
Must-visit: Royal Palace, Killing Fields, Tuol Sleng Genocide Museum
Riverfront: Sunset walks, night markets
Perfect for: History learners, budget travelers

INDONESIA
Bali:
Island of Gods. Budget: $35-70/day depending on area.
Regions:
- Ubud: Rice terraces, monkey forest, yoga retreats, art galleries
- Seminyak/Canggu: Beaches, surf, beach clubs, sunset bars
- Uluwatu: Clifftop temples, world-class surf breaks
Activities: Temple visits, rice terrace walks, volcano hikes (Mount Batur), diving
Best for: Wellness seekers, surfers, digital nomads, honeymooners

Jakarta:
Modern Indonesian capital. Budget: $40-60/day.
Sights: National Monument (Monas), Old Town (Kota Tua), Istiqlal Mosque
Food: Try nasi goreng, satay, rendang
Shopping: Malls and traditional markets

MALAYSIA
Kuala Lumpur:
Modern multicultural capital. Budget: $35-55/day.
Icons: Petronas Towers, Batu Caves, Central Market
Food: Hawker centers, try nasi lemak, laksa, roti canai
Perfect for: City breaks, diverse food scene, good value

Penang:
Food capital of Malaysia. Budget: $30-45/day.
Georgetown: UNESCO heritage site, street art, colonial architecture
Food: Best street food in Southeast Asia - char kway teow, hokkien mee
Beaches: Batu Ferringhi for beach resorts

SINGAPORE
City-state hub. Budget: $80-150/day (pricier).
Attractions: Marina Bay Sands, Gardens by the Bay, Sentosa Island, Hawker centers
Food: Affordable hawker food, Michelin-street food, high-end restaurants
Perfect for: Stopover destination, food lovers, safe introduction to Asia

PHILIPPINES
7,000+ islands paradise. Budget: $30-50/day.
Destinations:
- Palawan (El Nido, Coron): Limestone cliffs, lagoons, diving
- Boracay: White sand beaches (reopened after cleanup)
- Manila: Capital city, historical Intramuros
Activities: Island hopping, diving, snorkeling, beach relaxation
Best time: December-May (dry season)

LAOS
Luang Prabang:
Peaceful UNESCO town. Budget: $25-40/day.
Activities: Alms giving ceremony (dawn), Kuang Si waterfalls, night market
Temples: Wat Xieng Thong, Mount Phousi sunset
Perfect for: Slow travel, spiritual seekers, budget backpackers

MYANMAR (Burma)
Bagan:
Ancient temple city. Budget: $35-55/day.
Experience: Hot air balloon over 2,000 temples (expensive but worth it)
Activities: Temple exploration by e-bike, sunset viewpoints
Note: Check travel advisories before visiting

Regional Travel Tips:
- Visas: Most offer visa on arrival or e-visa. Check requirements.
- Transportation: Buses, trains, budget airlines (AirAsia, VietJet). Book ahead for popular routes.
- Accommodation: Hostels ($5-15), guesthouses ($15-30), hotels ($30-100+)
- Food: Street food ($1-3), local restaurants ($3-8), western food ($8-15)
- Best time: Generally November-February (cool and dry), avoid monsoon season
- SIM cards: Buy local SIM at airport, data very cheap
- Scams: Be aware but don't be paranoid. Research common scams.
- Respect: Dress modestly at temples, remove shoes when entering homes/temples
"""
}

def create_sample_documents():
    """Create sample travel documents in data folder"""
    print("🗺️  Creating sample travel data...")
    print("=" * 60)
    
    for filename, content in SAMPLE_DOCUMENTS.items():
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: {filename}")
    
    print("=" * 60)
    print(f"✨ Created {len(SAMPLE_DOCUMENTS)} sample documents in '{DATA_DIR}/' folder")
    print("\nThese documents will be automatically loaded when you start the server!")
    print("\nYou can add your own PDF or TXT files to the data/ folder:")
    print("  - Travel guides")
    print("  - Activity lists")
    print("  - Destination information")
    print("  - Language phrases")
    print("  - Cultural tips")
    print("\nRun 'python main.py' to start the server and load the data!")

if __name__ == "__main__":
    create_sample_documents()