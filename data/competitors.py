"""AppFolio competitive landscape knowledge base."""

DIRECT_COMPETITOR_NAMES = [
    "yardi", "realpage", "mri software", "entrata", "buildium",
    "rent manager", "resman", "propertyware", "doorloop", "turbotenant", "hemlane",
]
INDIRECT_COMPETITOR_NAMES = [
    "eliseai", "betterbot", "knock crm", "funnel leasing",
    "leadsimple", "rentvine", "rentec direct", "smartrent", "latch",
]
COMPETITOR_DOMAIN_KEYWORDS = [
    "property management software", "property management platform",
    "multifamily software", "leasing automation", "AI leasing assistant",
    "tenant screening", "rent collection", "maintenance requests",
    "property accounting", "HOA management", "rental property software",
    "residential property management", "proptech platform",
    "single-family rental software", "landlord software",
    "lease management", "vacancy management", "property manager tools",
]
APPFOLIO_CONTEXT = """
ABOUT APPFOLIO (APPF):
Products: AppFolio Property Manager, AppFolio Property Manager PLUS, AI Leasing Assistant (Lisa),
AppFolio Investment Management, AppFolio Stack.
Business model: SaaS per-unit pricing + payment processing fees.
Market position: fastest-growing mid-market residential PM platform (500-5,000 units).

DIRECT COMPETITORS: Yardi, RealPage, MRI Software, Entrata, Buildium, Rent Manager, ResMan, Propertyware, Doorloop, TurboTenant, Hemlane.
INDIRECT: EliseAI, BetterBot, Knock CRM, Funnel Leasing, LeadSimple, Rentvine, SmartRent, Latch.
EMERGING THREATS: AI-native PM platforms, Zillow Rental Manager, CoStar/Apartments.com vertical integration.

HIGH relevance: direct competitor raises funding/launches AI product/major customer win;
large PM group migrating away from AppFolio; AI leasing tool raises significant capital.
MEDIUM relevance: proptech raises Series B+ for leasing/PM automation;
VC thesis on rental housing tech; Yardi/RealPage bundles competing AI feature.
LOW (exclude): commercial real estate brokerage, mortgage tech, pre-seed under $5M, short-term rental platforms.
"""
