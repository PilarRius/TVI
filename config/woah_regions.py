"""WOAH regional commission membership (ISO3 → region).

Regions follow WOAH Regional Commissions:
  Africa | Americas | Asia and the Pacific | Europe | Middle East

Membership is approximate for prototype purposes and can be updated
from official WOAH Member lists without changing calculation code.
"""

from __future__ import annotations

WOAH_REGIONS = [
    "Africa",
    "Americas",
    "Asia and the Pacific",
    "Europe",
    "Middle East",
]

# ISO3 → WOAH region
ISO3_TO_REGION: dict[str, str] = {
    # --- Africa ---
    "DZA": "Africa", "AGO": "Africa", "BEN": "Africa", "BWA": "Africa",
    "BFA": "Africa", "BDI": "Africa", "CMR": "Africa", "CPV": "Africa",
    "CAF": "Africa", "TCD": "Africa", "COM": "Africa", "COG": "Africa",
    "COD": "Africa", "CIV": "Africa", "DJI": "Africa", "EGY": "Africa",
    "GNQ": "Africa", "ERI": "Africa", "SWZ": "Africa", "ETH": "Africa",
    "GAB": "Africa", "GMB": "Africa", "GHA": "Africa", "GIN": "Africa",
    "GNB": "Africa", "KEN": "Africa", "LSO": "Africa", "LBR": "Africa",
    "LBY": "Africa", "MDG": "Africa", "MWI": "Africa", "MLI": "Africa",
    "MRT": "Africa", "MUS": "Africa", "MAR": "Africa", "MOZ": "Africa",
    "NAM": "Africa", "NER": "Africa", "NGA": "Africa", "RWA": "Africa",
    "STP": "Africa", "SEN": "Africa", "SYC": "Africa", "SLE": "Africa",
    "SOM": "Africa", "ZAF": "Africa", "SSD": "Africa", "SDN": "Africa",
    "TZA": "Africa", "TGO": "Africa", "TUN": "Africa", "UGA": "Africa",
    "ZMB": "Africa", "ZWE": "Africa",
    # --- Americas ---
    "ATG": "Americas", "ARG": "Americas", "BHS": "Americas", "BRB": "Americas",
    "BLZ": "Americas", "BOL": "Americas", "BRA": "Americas", "CAN": "Americas",
    "CHL": "Americas", "COL": "Americas", "CRI": "Americas", "CUB": "Americas",
    "DMA": "Americas", "DOM": "Americas", "ECU": "Americas", "SLV": "Americas",
    "GRD": "Americas", "GTM": "Americas", "GUY": "Americas", "HTI": "Americas",
    "HND": "Americas", "JAM": "Americas", "MEX": "Americas", "NIC": "Americas",
    "PAN": "Americas", "PRY": "Americas", "PER": "Americas", "KNA": "Americas",
    "LCA": "Americas", "VCT": "Americas", "SUR": "Americas", "TTO": "Americas",
    "USA": "Americas", "URY": "Americas", "VEN": "Americas",
    # --- Asia and the Pacific ---
    "AFG": "Asia and the Pacific", "AUS": "Asia and the Pacific",
    "BGD": "Asia and the Pacific", "BTN": "Asia and the Pacific",
    "BRN": "Asia and the Pacific", "KHM": "Asia and the Pacific",
    "CHN": "Asia and the Pacific", "FJI": "Asia and the Pacific",
    "IND": "Asia and the Pacific", "IDN": "Asia and the Pacific",
    "JPN": "Asia and the Pacific", "KAZ": "Asia and the Pacific",
    "PRK": "Asia and the Pacific", "KOR": "Asia and the Pacific",
    "KGZ": "Asia and the Pacific", "LAO": "Asia and the Pacific",
    "MYS": "Asia and the Pacific", "MDV": "Asia and the Pacific",
    "MNG": "Asia and the Pacific", "MMR": "Asia and the Pacific",
    "NPL": "Asia and the Pacific", "NZL": "Asia and the Pacific",
    "PAK": "Asia and the Pacific", "PNG": "Asia and the Pacific",
    "PHL": "Asia and the Pacific", "SGP": "Asia and the Pacific",
    "LKA": "Asia and the Pacific", "TWN": "Asia and the Pacific",
    "TJK": "Asia and the Pacific", "THA": "Asia and the Pacific",
    "TLS": "Asia and the Pacific", "TKM": "Asia and the Pacific",
    "UZB": "Asia and the Pacific", "VNM": "Asia and the Pacific",
    "WSM": "Asia and the Pacific", "VUT": "Asia and the Pacific",
    "TON": "Asia and the Pacific", "SLB": "Asia and the Pacific",
    # --- Europe ---
    "ALB": "Europe", "AND": "Europe", "ARM": "Europe", "AUT": "Europe",
    "AZE": "Europe", "BLR": "Europe", "BEL": "Europe", "BIH": "Europe",
    "BGR": "Europe", "HRV": "Europe", "CYP": "Europe", "CZE": "Europe",
    "DNK": "Europe", "EST": "Europe", "FIN": "Europe", "FRA": "Europe",
    "GEO": "Europe", "DEU": "Europe", "GRC": "Europe", "HUN": "Europe",
    "ISL": "Europe", "IRL": "Europe", "ISR": "Europe", "ITA": "Europe",
    "XKX": "Europe", "LVA": "Europe", "LIE": "Europe", "LTU": "Europe",
    "LUX": "Europe", "MLT": "Europe", "MDA": "Europe", "MCO": "Europe",
    "MNE": "Europe", "NLD": "Europe", "MKD": "Europe", "NOR": "Europe",
    "POL": "Europe", "PRT": "Europe", "ROU": "Europe", "RUS": "Europe",
    "SMR": "Europe", "SRB": "Europe", "SVK": "Europe", "SVN": "Europe",
    "ESP": "Europe", "SWE": "Europe", "CHE": "Europe", "TUR": "Europe",
    "UKR": "Europe", "GBR": "Europe", "VAT": "Europe",
    # --- Middle East ---
    "BHR": "Middle East", "IRN": "Middle East", "IRQ": "Middle East",
    "JOR": "Middle East", "KWT": "Middle East", "LBN": "Middle East",
    "OMN": "Middle East", "PSE": "Middle East", "QAT": "Middle East",
    "SAU": "Middle East", "SYR": "Middle East", "ARE": "Middle East",
    "YEM": "Middle East",
}

# Display names (ISO3 → English short name)
ISO3_TO_NAME: dict[str, str] = {
    "AFG": "Afghanistan", "ALB": "Albania", "DZA": "Algeria", "AND": "Andorra",
    "AGO": "Angola", "ATG": "Antigua and Barbuda", "ARG": "Argentina",
    "ARM": "Armenia", "AUS": "Australia", "AUT": "Austria", "AZE": "Azerbaijan",
    "BHS": "Bahamas", "BHR": "Bahrain", "BGD": "Bangladesh", "BRB": "Barbados",
    "BLR": "Belarus", "BEL": "Belgium", "BLZ": "Belize", "BEN": "Benin",
    "BTN": "Bhutan", "BOL": "Bolivia", "BIH": "Bosnia and Herzegovina",
    "BWA": "Botswana", "BRA": "Brazil", "BRN": "Brunei", "BGR": "Bulgaria",
    "BFA": "Burkina Faso", "BDI": "Burundi", "CPV": "Cabo Verde",
    "KHM": "Cambodia", "CMR": "Cameroon", "CAN": "Canada",
    "CAF": "Central African Republic", "TCD": "Chad", "CHL": "Chile",
    "CHN": "China", "COL": "Colombia", "COM": "Comoros", "COG": "Congo",
    "COD": "Democratic Republic of the Congo", "CRI": "Costa Rica",
    "CIV": "Côte d'Ivoire", "HRV": "Croatia", "CUB": "Cuba", "CYP": "Cyprus",
    "CZE": "Czechia", "DNK": "Denmark", "DJI": "Djibouti", "DMA": "Dominica",
    "DOM": "Dominican Republic", "ECU": "Ecuador", "EGY": "Egypt",
    "SLV": "El Salvador", "GNQ": "Equatorial Guinea", "ERI": "Eritrea",
    "EST": "Estonia", "SWZ": "Eswatini", "ETH": "Ethiopia", "FJI": "Fiji",
    "FIN": "Finland", "FRA": "France", "GAB": "Gabon", "GMB": "Gambia",
    "GEO": "Georgia", "DEU": "Germany", "GHA": "Ghana", "GRC": "Greece",
    "GRD": "Grenada", "GTM": "Guatemala", "GIN": "Guinea", "GNB": "Guinea-Bissau",
    "GUY": "Guyana", "HTI": "Haiti", "HND": "Honduras", "HUN": "Hungary",
    "ISL": "Iceland", "IND": "India", "IDN": "Indonesia", "IRN": "Iran",
    "IRQ": "Iraq", "IRL": "Ireland", "ISR": "Israel", "ITA": "Italy",
    "JAM": "Jamaica", "JPN": "Japan", "JOR": "Jordan", "KAZ": "Kazakhstan",
    "KEN": "Kenya", "KOR": "Republic of Korea", "PRK": "Dem. People's Rep. of Korea",
    "KWT": "Kuwait", "KGZ": "Kyrgyzstan", "LAO": "Lao PDR", "LVA": "Latvia",
    "LBN": "Lebanon", "LSO": "Lesotho", "LBR": "Liberia", "LBY": "Libya",
    "LIE": "Liechtenstein", "LTU": "Lithuania", "LUX": "Luxembourg",
    "MDG": "Madagascar", "MWI": "Malawi", "MYS": "Malaysia", "MDV": "Maldives",
    "MLI": "Mali", "MLT": "Malta", "MRT": "Mauritania", "MUS": "Mauritius",
    "MEX": "Mexico", "MDA": "Moldova", "MCO": "Monaco", "MNG": "Mongolia",
    "MNE": "Montenegro", "MAR": "Morocco", "MOZ": "Mozambique", "MMR": "Myanmar",
    "NAM": "Namibia", "NPL": "Nepal", "NLD": "Netherlands", "NZL": "New Zealand",
    "NIC": "Nicaragua", "NER": "Niger", "NGA": "Nigeria", "MKD": "North Macedonia",
    "NOR": "Norway", "OMN": "Oman", "PAK": "Pakistan", "PAN": "Panama",
    "PNG": "Papua New Guinea", "PRY": "Paraguay", "PER": "Peru",
    "PHL": "Philippines", "POL": "Poland", "PRT": "Portugal", "QAT": "Qatar",
    "ROU": "Romania", "RUS": "Russian Federation", "RWA": "Rwanda",
    "KNA": "Saint Kitts and Nevis", "LCA": "Saint Lucia",
    "VCT": "Saint Vincent and the Grenadines", "WSM": "Samoa",
    "SMR": "San Marino", "STP": "Sao Tome and Principe", "SAU": "Saudi Arabia",
    "SEN": "Senegal", "SRB": "Serbia", "SYC": "Seychelles", "SLE": "Sierra Leone",
    "SGP": "Singapore", "SVK": "Slovakia", "SVN": "Slovenia", "SLB": "Solomon Islands",
    "SOM": "Somalia", "ZAF": "South Africa", "SSD": "South Sudan", "ESP": "Spain",
    "LKA": "Sri Lanka", "SDN": "Sudan", "SUR": "Suriname", "SWE": "Sweden",
    "CHE": "Switzerland", "SYR": "Syria", "TWN": "Chinese Taipei",
    "TJK": "Tajikistan", "TZA": "Tanzania", "THA": "Thailand", "TLS": "Timor-Leste",
    "TGO": "Togo", "TON": "Tonga", "TTO": "Trinidad and Tobago", "TUN": "Tunisia",
    "TUR": "Türkiye", "TKM": "Turkmenistan", "UGA": "Uganda", "UKR": "Ukraine",
    "ARE": "United Arab Emirates", "GBR": "United Kingdom",
    "USA": "United States of America", "URY": "Uruguay", "UZB": "Uzbekistan",
    "VUT": "Vanuatu", "VEN": "Venezuela", "VNM": "Viet Nam", "YEM": "Yemen",
    "ZMB": "Zambia", "ZWE": "Zimbabwe", "PSE": "Palestine", "XKX": "Kosovo",
    "VAT": "Holy See",
}


def region_for(iso3: str) -> str | None:
    return ISO3_TO_REGION.get(iso3)


def name_for(iso3: str) -> str:
    return ISO3_TO_NAME.get(iso3, iso3)
