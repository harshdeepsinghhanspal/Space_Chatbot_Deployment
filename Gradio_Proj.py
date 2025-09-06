#PYHTON 3.9
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pathlib

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

#MEMORY
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain


import re

import mimetypes
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")

# List of space-related keywords (for filtering queries)
space_keywords = [
    # Basic space terms
    "space", "nasa", "moon", "planet", "mars", "venus", "jupiter", "saturn", "neptune", "mercury",
    "galaxy", "universe", "astronomy", "black hole", "blackhole", "telescope", "astronaut", "orbit",
    "iss", "stars", "milky way", "cosmos", "rocket", "gravity", "meteor", "comet", "nebula", "eclipse","sun","betelgeuse",
    # Space agencies & organizations
    "nasa", "isro", "roscosmos", "esa", "jaxa", "dlr", "arianespace", "space force",
    "cnsa", "supaarco", "cnes", "uksa", "asi", "isa", "ksa", "kari", "uaesa", "angkasawan", "conae",
    "cltc", "anasis", "supsi", "ssc", "nsau", "canadian space agency", "csa", "aeb", "lapan",
    "turkish space agency", "tua", "austrian space agency", "belgian institute for space aeronomy",
    "norwegian space agency", "luxembourg space agency", "lsa", "thai space agency", "gistda",
    "nigerian space research and development agency", "nasrda", "egyptian space agency", "egsa",
    #astronauts
    "yuri gagarin", "neil armstrong", "buzz aldrin", "valentina tereshkova",
    "alan shepard", "john glenn", "ed white", "frank borman", "jim lovell",
    "william anders", "michael collins", "david scott", "james irwin",
    "ronald evans", "don eisele", "joe engle", "jeanette epps", 
    "joe edwards", "tracy caldwell", "clayton anderson", "michael foreman",
    "scott kelly", "mark kelly", "sunita williams", "peggy whitson",
    "christina koch", "jessica meir", "chris hadfield", "luca parmitano",
    "jean-loup chrétien", "claudie haignere", "wubbo ockels", "sigmund jahn",
    "vladimír remek", "rakesh sharma", "pham tuan", "arnaldo tamayo mendez",
    "guion bluford", "franklin chang-diaz", "helen sharman", "marcos pontes",
    "pedro duque", "yi so-yeon", "sultan ibn salman al saud", "marc garneau",
    "julie payette", "robert thirsk", "ilian ramon", "raja chari",
    "anil menon", "kalpana chawla", "hazza al mansouri", "anousheh ansari",
    "dennis tito", "mark shuttleworth", "gregory olsen", "charles simonyi",
    "richard garriott", "guy laliberté", "yusaku maezawa", "jared isaacman",
    "mike melvill", "edgar mitchell", "fred haise", "jack swigert",
    "stuart roosa", "al worden", "ken mattingly", "tom stafford",
    "frank de winne", "andre kuipers", "paolo nespoli", "hans schlegel",
    "roberto vittori", "leopold eyharts", "mikhail kornienko", 
    "yury lonchakov", "sergei volkov", "aleksandr skvortsov",
    "dmitri kondratyev", "paul richards", "ivan bella", "michal fulier",
    "chen quan", "fei junlong", "yang liwei", "zhai zhigang",
    "nie haisheng", "liu wang", "jing haipeng", "liu boming",
    "rai barnawi", "ali alqarni", "mariam fardous", "alper gezeravci",
    "tuva cihangir atasever", "katherine bennell pegg", "sophie adenot",
    "pablo alvarez fernandez",
    "serena aunon-chancellor", "victor glover", "kate rubins", "doug hurley",
    "bob behnken", "ellen ochoa", "mae jemison", "janet kavandi", "stephanie wilson",
    "jessica watkins", "jeremy hansen", "takuya onishi", "koichi wakata", 
    "akihiko hoshide", "soichi noguchi", "nicole mann", "michael hopkins",
    "shannon walker", "thomas pesquet", "alexander gerst", "samantha cristoforetti",
    # Famous scientists and pioneers in space science
    "vikram sarabhai", "abdul kalam", "satish dhawan", "k kasturirangan", "ur rao",
    "mylswamy annadurai", "k sivan", "s somanath", "radhakrishnan kappagantu", "tessy thomas",
    "anuradha tk", "n valarmathi", "m annadurai", "ritu karidhal", "mangala mani",
    "narendra bhardwaj", "suresh nair", "a s kiran kumar", "jayant narlikar",
    "subrahmanyan chandrasekhar", "meghnad saha", "venkatraman radhakrishnan",
    "bhaskaracharya", "aryabhata", "brahmagupta", "galileo galilei", "johannes kepler", 
    "nicolaus copernicus", "isaac newton", "albert einstein", "stephen hawking", "carl sagan", 
    "edwin hubble", "neil degrasse tyson", "abdus salam", "wernher von braun", "sergei korolev", 
    "valentina tereshkova", "yuri gagarin", "buzz aldrin", "katherine johnson", "annie easley", 
    "claude nicollier", "marcos pontes", "christer fuglesang", "mae jemison", "ellen ochoa", 
    "helen sharman", "jean-loup chrétien", "qian xuesen", "hermann oberth", "elena kondakova",
    # Companies & private spaceflight
    "spacex", "blue origin", "virgin galactic", "rocket lab", "relativity space", "skyroot",
    "agnikul", "axiom", "firefly", "planet labs", "ghadar", "expace", "satellogic", "spinlaunch",
    "starlabs", "rancholabs",
    # Famous missions & spacecraft
    "apollo", "chandrayaan", "gaganyaan", "artemis", "perseverance", "vikram", "voyager", "juno",
    "new horizons", "hubble", "james webb", "jwst", "lander", "rover", "probe", "cube sat",
    "nano satellite", "balloon satellite", "sounding rocket", "vyomanaut",
    # Theoretical physics and cosmology
    "relativity", "einstein", "einstein field equations", "event horizon", "singularity",
    "wormhole", "hawking", "hawking radiation", "space-time", "curvature", "gravitational lensing",
    "dark matter", "dark energy", "cosmic microwave background", "cmb", "multiverse", "entropy",
    "redshift", "blueshift", "time dilation", "blackbody radiation", "twin paradox", "quantum foam",
    "loop quantum gravity", "string theory", "brane", "inflation", "big bang", "heat death",
    "casimir effect", "no-hair theorem", "penrose process", "frame dragging", "kerr metric",
    "reissner-nordström", "metric tensor", "cosmological constant", "lambda cold dark matter",
    "baryonic matter", "neutrino", "graviton", "quantum tunneling", "feynman diagram",
    "hubble constant", "olbers paradox", "cosmic expansion", "observable universe", "light cone",
    "past light cone", "future event horizon", "infinity",
    # Planets & dwarf planets
    "mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto",
    "ceres", "eris", "haumea", "makemake",
    # Satellites (not including deep space missions listed later)
    "aryabhata", "bhaskara", "rohini", "insat", "gsat", "irs", "cartosat", "risat", "ocean sat",
    "navic", "kalpana-1", "mangalyaan", "chandrayaan-1", "chandrayaan-2", "chandrayaan-3",
    "sentinel", "landsat", "terra", "aqua", "aura", "envisat", "goes", "meteosat", "himawari",
    "noaa",
    # Rovers
    "sojourner", "spirit", "opportunity", "curiosity", "perseverance", "pragyan", "zhurong",
    "luna 17", "luna 21", "yaoki", "rashid", "exomars rover", "marsokhod", "resource prospector",
    "volatiles investigating polar exploration rover", "viper",
    # Rockets / Launch vehicles
    "pslv", "gslv", "gslv mk iii", "lvm3", "agni", "slv", "aslv", "falcon 1", "falcon 9",
    "falcon heavy", "starship", "sls", "atlas v", "delta iv", "ariane 5", "ariane 6",
    "soyuz", "zenit", "long march", "vega", "electron", "h3", "pegasus", "minotaur", "antares",
    "new shepard", "new glenn", "rs1", "skyroot vikram", "agniKul cosmos", "neutron", "vulcan centaur",
    # Missions, probes, tools
    "apollo", "chandrayaan", "gaganyaan", "artemis", "perseverance", "vikram", "voyager",
    "juno", "new horizons", "hubble", "james webb", "jwst", "lander", "rover", "probe",
    "cube sat", "nano satellite", "balloon satellite", "sounding rocket", "galileo", "kepler",
    "tess", "spitzer", "pioneer", "mariner", "cassini", "galileo spacecraft", "bepi colombo",
    "osiris-rex", "dart", "insight", "helios", "lunar orbiter", "lunar gateway", "lupex",
    # Moons
    "io", "europa", "ganymede", "callisto", "titan", "enceladus", "triton", "phoebe", "charon",
    "phobos", "deimos",
    # Planetary features
    "olympus mons", "valles marineris", "hellas basin", "mare", "planitia", "mons", "terra",
    "tholus", "impact crater", "lava tube", "ice cap", "subsurface ocean",
    # Star types & life cycle
    "supernova", "nova", "neutron star", "pulsar", "quasar", "white dwarf", "red dwarf",
    "brown dwarf", "red giant", "main sequence", "protostar", "stellar nursery",
    # Exoplanets & extraterrestrial life
    "exoplanet", "habitable zone", "kepler", "trappist-1", "proxima b", "biosignature",
    "astrobiology", "drake equation", "fermi paradox", "extraterrestrial", "alien",
    "ufo", "ufology", "SETI", "wow signal",
    # Interstellar & intergalactic
    "interstellar", "intergalactic", "interstellar probe", "andromeda", "magellanic cloud",
    "void", "filament", "supercluster",
    # Propulsion systems & future concepts
    "ion drive", "solar sail", "warp drive", "antimatter engine", "light sail",
    "generation ship", "dyson sphere", "von neumann probe",
    # Space environment & hazards
    "cosmic rays", "solar wind", "radiation belt", "van allen belt", "heliosphere",
    "bow shock", "space weather", "micrometeoroid", "space debris", "microgravity",
    "zero gravity",
    # Measurement & units
    "astronomical unit", "light year", "planck length", "planck time", "heliocentric",
    "geocentric",
    # Observatories & telescopes
    "alma", "chandra", "keck", "gaia", "planck telescope", "spitzer", "infrared telescope",
    # Other celestial objects
    "minor planet", "meteoroid", "bolide", "open cluster",
    # Space tech & systems
    "spacesuit", "spacewalk", "extravehicular activity", "life support system", "planetary ring",
    "ring system",
    # Fiction & cultural references
    "2001 a space odyssey", "star trek","starwars", "star wars", "the expanse", "x-files", "contact",
    # Colonization & infrastructure
    "terraforming", "space colonization", "space elevator"
]

app = FastAPI()
# Serve static files (CSS + JS)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


# Add CORS so the frontend can access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the environment variable for the GROQ API key
os.environ["GROQ_API_KEY"] = "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"

llm = ChatGroq(
    temperature=0.3,
    model_name="llama-3.3-70b-versatile",
    max_tokens=512
)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a knowledgeable and concise assistant specialized in answering questions related to space and astronomy. "
     "You can explain concepts about planets, rockets, satellites, space agencies, astronauts, scientists, cosmology, astrophysics, and extraterrestrial phenomena. "
     "Only respond to space-related topics and ignore unrelated queries. Avoid repeating sentences or phrases in your responses. Be accurate, brief, and clear."),
    ("user", "{input}")
])

#MEMORY
memory = ConversationBufferMemory(return_messages=True)

conversation_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    verbose=True
)

chain = prompt | llm | StrOutputParser()

class Query(BaseModel):
    message: str

from fastapi.responses import FileResponse

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse("index.html")

# Clean up repeated lines or repeated phrases
def cleanup_response(text: str) -> str:
    # Remove **bold** and *italic*
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)

    # Deduplicate lines
    lines = text.split("\n")
    seen = set()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped not in seen:
            cleaned.append(stripped)
            seen.add(stripped)
    
    result = "\n".join(cleaned)

    # Safely clip to ~512 tokens = approx 2000 characters
    if len(result) > 2000:
        # Cut at last complete sentence before 2000 characters
        truncated = result[:2000]
        last_dot = truncated.rfind(".")
        if last_dot != -1:
            result = truncated[:last_dot + 1]
        else:
            result = truncated  # fallback

    return result

# Main endpoint for answering space-related queries
@app.post("/ask")
async def ask_spacebot(query: Query):
    user_input = query.message
    #PYHTON 3.9
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pathlib

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

#MEMORY
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain


import re

import mimetypes
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")

# List of space-related keywords (for filtering queries)
space_keywords = [
    # Basic space terms
    "space", "nasa", "moon", "planet", "mars", "venus", "jupiter", "saturn", "neptune", "mercury",
    "galaxy", "universe", "astronomy", "black hole", "blackhole", "telescope", "astronaut", "orbit",
    "iss", "stars", "milky way", "cosmos", "rocket", "gravity", "meteor", "comet", "nebula", "eclipse","sun","betelgeuse",
    # Space agencies & organizations
    "nasa", "isro", "roscosmos", "esa", "jaxa", "dlr", "arianespace", "space force",
    "cnsa", "supaarco", "cnes", "uksa", "asi", "isa", "ksa", "kari", "uaesa", "angkasawan", "conae",
    "cltc", "anasis", "supsi", "ssc", "nsau", "canadian space agency", "csa", "aeb", "lapan",
    "turkish space agency", "tua", "austrian space agency", "belgian institute for space aeronomy",
    "norwegian space agency", "luxembourg space agency", "lsa", "thai space agency", "gistda",
    "nigerian space research and development agency", "nasrda", "egyptian space agency", "egsa",
    #astronauts
    "yuri gagarin", "neil armstrong", "buzz aldrin", "valentina tereshkova",
    "alan shepard", "john glenn", "ed white", "frank borman", "jim lovell",
    "william anders", "michael collins", "david scott", "james irwin",
    "ronald evans", "don eisele", "joe engle", "jeanette epps", 
    "joe edwards", "tracy caldwell", "clayton anderson", "michael foreman",
    "scott kelly", "mark kelly", "sunita williams", "peggy whitson",
    "christina koch", "jessica meir", "chris hadfield", "luca parmitano",
    "jean-loup chrétien", "claudie haignere", "wubbo ockels", "sigmund jahn",
    "vladimír remek", "rakesh sharma", "pham tuan", "arnaldo tamayo mendez",
    "guion bluford", "franklin chang-diaz", "helen sharman", "marcos pontes",
    "pedro duque", "yi so-yeon", "sultan ibn salman al saud", "marc garneau",
    "julie payette", "robert thirsk", "ilian ramon", "raja chari",
    "anil menon", "kalpana chawla", "hazza al mansouri", "anousheh ansari",
    "dennis tito", "mark shuttleworth", "gregory olsen", "charles simonyi",
    "richard garriott", "guy laliberté", "yusaku maezawa", "jared isaacman",
    "mike melvill", "edgar mitchell", "fred haise", "jack swigert",
    "stuart roosa", "al worden", "ken mattingly", "tom stafford",
    "frank de winne", "andre kuipers", "paolo nespoli", "hans schlegel",
    "roberto vittori", "leopold eyharts", "mikhail kornienko", 
    "yury lonchakov", "sergei volkov", "aleksandr skvortsov",
    "dmitri kondratyev", "paul richards", "ivan bella", "michal fulier",
    "chen quan", "fei junlong", "yang liwei", "zhai zhigang",
    "nie haisheng", "liu wang", "jing haipeng", "liu boming",
    "rai barnawi", "ali alqarni", "mariam fardous", "alper gezeravci",
    "tuva cihangir atasever", "katherine bennell pegg", "sophie adenot",
    "pablo alvarez fernandez",
    "serena aunon-chancellor", "victor glover", "kate rubins", "doug hurley",
    "bob behnken", "ellen ochoa", "mae jemison", "janet kavandi", "stephanie wilson",
    "jessica watkins", "jeremy hansen", "takuya onishi", "koichi wakata", 
    "akihiko hoshide", "soichi noguchi", "nicole mann", "michael hopkins",
    "shannon walker", "thomas pesquet", "alexander gerst", "samantha cristoforetti",
    # Famous scientists and pioneers in space science
    "vikram sarabhai", "abdul kalam", "satish dhawan", "k kasturirangan", "ur rao",
    "mylswamy annadurai", "k sivan", "s somanath", "radhakrishnan kappagantu", "tessy thomas",
    "anuradha tk", "n valarmathi", "m annadurai", "ritu karidhal", "mangala mani",
    "narendra bhardwaj", "suresh nair", "a s kiran kumar", "jayant narlikar",
    "subrahmanyan chandrasekhar", "meghnad saha", "venkatraman radhakrishnan",
    "bhaskaracharya", "aryabhata", "brahmagupta", "galileo galilei", "johannes kepler", 
    "nicolaus copernicus", "isaac newton", "albert einstein", "stephen hawking", "carl sagan", 
    "edwin hubble", "neil degrasse tyson", "abdus salam", "wernher von braun", "sergei korolev", 
    "valentina tereshkova", "yuri gagarin", "buzz aldrin", "katherine johnson", "annie easley", 
    "claude nicollier", "marcos pontes", "christer fuglesang", "mae jemison", "ellen ochoa", 
    "helen sharman", "jean-loup chrétien", "qian xuesen", "hermann oberth", "elena kondakova",
    # Companies & private spaceflight
    "spacex", "blue origin", "virgin galactic", "rocket lab", "relativity space", "skyroot",
    "agnikul", "axiom", "firefly", "planet labs", "ghadar", "expace", "satellogic", "spinlaunch",
    "starlabs", "rancholabs",
    # Famous missions & spacecraft
    "apollo", "chandrayaan", "gaganyaan", "artemis", "perseverance", "vikram", "voyager", "juno",
    "new horizons", "hubble", "james webb", "jwst", "lander", "rover", "probe", "cube sat",
    "nano satellite", "balloon satellite", "sounding rocket", "vyomanaut",
    # Theoretical physics and cosmology
    "relativity", "einstein", "einstein field equations", "event horizon", "singularity",
    "wormhole", "hawking", "hawking radiation", "space-time", "curvature", "gravitational lensing",
    "dark matter", "dark energy", "cosmic microwave background", "cmb", "multiverse", "entropy",
    "redshift", "blueshift", "time dilation", "blackbody radiation", "twin paradox", "quantum foam",
    "loop quantum gravity", "string theory", "brane", "inflation", "big bang", "heat death",
    "casimir effect", "no-hair theorem", "penrose process", "frame dragging", "kerr metric",
    "reissner-nordström", "metric tensor", "cosmological constant", "lambda cold dark matter",
    "baryonic matter", "neutrino", "graviton", "quantum tunneling", "feynman diagram",
    "hubble constant", "olbers paradox", "cosmic expansion", "observable universe", "light cone",
    "past light cone", "future event horizon", "infinity",
    # Planets & dwarf planets
    "mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto",
    "ceres", "eris", "haumea", "makemake",
    # Satellites (not including deep space missions listed later)
    "aryabhata", "bhaskara", "rohini", "insat", "gsat", "irs", "cartosat", "risat", "ocean sat",
    "navic", "kalpana-1", "mangalyaan", "chandrayaan-1", "chandrayaan-2", "chandrayaan-3",
    "sentinel", "landsat", "terra", "aqua", "aura", "envisat", "goes", "meteosat", "himawari",
    "noaa",
    # Rovers
    "sojourner", "spirit", "opportunity", "curiosity", "perseverance", "pragyan", "zhurong",
    "luna 17", "luna 21", "yaoki", "rashid", "exomars rover", "marsokhod", "resource prospector",
    "volatiles investigating polar exploration rover", "viper",
    # Rockets / Launch vehicles
    "pslv", "gslv", "gslv mk iii", "lvm3", "agni", "slv", "aslv", "falcon 1", "falcon 9",
    "falcon heavy", "starship", "sls", "atlas v", "delta iv", "ariane 5", "ariane 6",
    "soyuz", "zenit", "long march", "vega", "electron", "h3", "pegasus", "minotaur", "antares",
    "new shepard", "new glenn", "rs1", "skyroot vikram", "agniKul cosmos", "neutron", "vulcan centaur",
    # Missions, probes, tools
    "apollo", "chandrayaan", "gaganyaan", "artemis", "perseverance", "vikram", "voyager",
    "juno", "new horizons", "hubble", "james webb", "jwst", "lander", "rover", "probe",
    "cube sat", "nano satellite", "balloon satellite", "sounding rocket", "galileo", "kepler",
    "tess", "spitzer", "pioneer", "mariner", "cassini", "galileo spacecraft", "bepi colombo",
    "osiris-rex", "dart", "insight", "helios", "lunar orbiter", "lunar gateway", "lupex",
    # Moons
    "io", "europa", "ganymede", "callisto", "titan", "enceladus", "triton", "phoebe", "charon",
    "phobos", "deimos",
    # Planetary features
    "olympus mons", "valles marineris", "hellas basin", "mare", "planitia", "mons", "terra",
    "tholus", "impact crater", "lava tube", "ice cap", "subsurface ocean",
    # Star types & life cycle
    "supernova", "nova", "neutron star", "pulsar", "quasar", "white dwarf", "red dwarf",
    "brown dwarf", "red giant", "main sequence", "protostar", "stellar nursery",
    # Exoplanets & extraterrestrial life
    "exoplanet", "habitable zone", "kepler", "trappist-1", "proxima b", "biosignature",
    "astrobiology", "drake equation", "fermi paradox", "extraterrestrial", "alien",
    "ufo", "ufology", "SETI", "wow signal",
    # Interstellar & intergalactic
    "interstellar", "intergalactic", "interstellar probe", "andromeda", "magellanic cloud",
    "void", "filament", "supercluster",
    # Propulsion systems & future concepts
    "ion drive", "solar sail", "warp drive", "antimatter engine", "light sail",
    "generation ship", "dyson sphere", "von neumann probe",
    # Space environment & hazards
    "cosmic rays", "solar wind", "radiation belt", "van allen belt", "heliosphere",
    "bow shock", "space weather", "micrometeoroid", "space debris", "microgravity",
    "zero gravity",
    # Measurement & units
    "astronomical unit", "light year", "planck length", "planck time", "heliocentric",
    "geocentric",
    # Observatories & telescopes
    "alma", "chandra", "keck", "gaia", "planck telescope", "spitzer", "infrared telescope",
    # Other celestial objects
    "minor planet", "meteoroid", "bolide", "open cluster",
    # Space tech & systems
    "spacesuit", "spacewalk", "extravehicular activity", "life support system", "planetary ring",
    "ring system",
    # Fiction & cultural references
    "2001 a space odyssey", "star trek","starwars", "star wars", "the expanse", "x-files", "contact",
    # Colonization & infrastructure
    "terraforming", "space colonization", "space elevator"
]

app = FastAPI()
# Serve static files (CSS + JS)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


# Add CORS so the frontend can access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the environment variable for the GROQ API key
os.environ["GROQ_API_KEY"] = "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"

llm = ChatGroq(
    temperature=0.3,
    model_name="llama-3.3-70b-versatile",
    max_tokens=512
)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a knowledgeable and concise assistant specialized in answering questions related to space and astronomy. "
     "You can explain concepts about planets, rockets, satellites, space agencies, astronauts, scientists, cosmology, astrophysics, and extraterrestrial phenomena. "
     "Only respond to space-related topics and ignore unrelated queries. Avoid repeating sentences or phrases in your responses. Be accurate, brief, and clear."),
    ("user", "{input}")
])

#MEMORY
memory = ConversationBufferMemory(return_messages=True)

conversation_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    verbose=True
)

chain = prompt | llm | StrOutputParser()

class Query(BaseModel):
    message: str

from fastapi.responses import FileResponse

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse("index.html")

# Clean up repeated lines or repeated phrases
def cleanup_response(text: str) -> str:
    # Remove **bold** and *italic*
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)

    # Deduplicate lines
    lines = text.split("\n")
    seen = set()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped not in seen:
            cleaned.append(stripped)
            seen.add(stripped)
    
    result = "\n".join(cleaned)

    # Safely clip to ~512 tokens = approx 2000 characters
    if len(result) > 2000:
        # Cut at last complete sentence before 2000 characters
        truncated = result[:2000]
        last_dot = truncated.rfind(".")
        if last_dot != -1:
            result = truncated[:last_dot + 1]
        else:
            result = truncated  # fallback

    return result

# Main endpoint for answering space-related queries
@app.post("/ask")
async def ask_spacebot(query: Query):
    user_input = query.message
    
    # Allow any question if previous context exists
    if not any(keyword in user_input.lower() for keyword in space_keywords):
        if not memory.buffer:  # if no prior conversation
            return {"response": "🚀 Please ask about space-related topics only!"}
    try:
        answer = conversation_chain.run(input=user_input)  # memory-aware
        answer = cleanup_response(answer)
        return {"response": answer}
    except Exception as e:
        return {"response": f"❌ Error: {str(e)}"}

#CLEARING MEMORY    
@app.post("/clear")
async def clear_memory():
    memory.clear()   # Clears stored chat history
    return {"response": "🧹 Memory cleared!"}
