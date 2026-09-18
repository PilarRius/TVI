"""Opening About / Methodology narrative (project framing before dimension detail)."""

from __future__ import annotations

from htmltools import HTML, TagList, tags


def methodology_intro_section() -> TagList:
    """Summarised project framing placed above the three dimension sections."""
    return TagList(
        tags.h2("About the Trade Vulnerability Index"),
        tags.p(
            "Animal-health shocks are an increasingly important source of disruption to food "
            "systems and economies. Emerging diseases, the re-emergence and spread of existing "
            "diseases into new areas, and changing transmission patterns are increasing pressure "
            "on governments and the private sector to prevent, manage and respond to "
            "animal-health threats."
        ),
        tags.p(
            "Outbreaks can reduce livestock production and household incomes, threaten food "
            "availability and affordability, and disrupt supply chains and international trade. "
            "Where diseases are zoonotic, they may also pose direct risks to human health. Effects "
            "can therefore extend well beyond the farms directly affected — to national economies "
            "and, through interconnected production and trade networks, to other countries. This "
            "interconnectedness of animal health, human wellbeing, food systems and economic "
            "activity is the One Health context in which such shocks need to be understood and "
            "managed."
        ),
        tags.p(
            "This project responds to ",
            tags.strong(
                "WOAH Datathon Challenge 4 — Trade Vulnerability and Disease Risk Along Trade "
                "and Movement Networks"
            ),
            ", which asks how animal-health events interact with trade and movement networks to "
            "generate vulnerability and disruption, and how better use of data can support trade "
            "resilience and risk-based decision-making.",
        ),
        tags.h3("Why a multidimensional index?"),
        tags.p(
            "A country’s vulnerability to an animal-health shock is multidimensional. It depends "
            "not only on the likelihood that a disease will reach or spread within the country, "
            "but also on how economically sensitive the country is to the resulting disruption, "
            "and on whether legal arrangements can help prevent, contain or mitigate effects on "
            "trade."
        ),
        tags.p(
            "The Trade Vulnerability Index for Animal-Health Shocks brings together data that are "
            "often collected and analysed separately — on ",
            tags.strong("disease exposure"),
            ", ",
            tags.strong("economic sensitivity"),
            " and ",
            tags.strong("legal preparedness"),
            " — into one comparative framework and dashboard. The added value is not creating "
            "entirely new datasets, but connecting existing sources so that relationships and "
            "vulnerabilities that are hard to see in isolation become visible.",
        ),
        tags.h3("Who it is for"),
        tags.p(
            "A common methodology across countries would allow governments, investors, the private "
            "sector, international organisations and development partners to see a country’s "
            "position relative to others and to identify the factors driving its vulnerability. "
            "Beyond benchmarking, a transparent profile could help build the case for legal and "
            "policy reform, prioritise investments in animal-health and trade infrastructure, "
            "support proposals for technical assistance and development finance, and inform trade "
            "and sanitary negotiations — including regionalisation, compartmentalisation and "
            "bilateral or regional arrangements that reduce future trade disruption."
        ),
        tags.p(
            "More broadly, by making vulnerability visible and comparable, the Index aims to "
            "shift animal-health preparedness from a largely reactive exercise toward identifying "
            "weaknesses before a crisis and directing policy, investment and international support "
            "where they are most needed."
        ),
        tags.h3("Research question and approach"),
        tags.p(
            tags.em(
                "How vulnerable is Country X to the trade-related consequences of an "
                "animal-health shock caused by Disease X?"
            )
        ),
        tags.p("Each dimension answers a specific question:"),
        tags.ul(
            tags.li(
                TagList(
                    tags.strong("Disease exposure: "),
                    "How exposed is the country to the introduction or spread of the disease?",
                )
            ),
            tags.li(
                TagList(
                    tags.strong("Economic sensitivity: "),
                    "How strongly could the country’s economy or relevant livestock sector be "
                    "affected if the shock materialises?",
                )
            ),
            tags.li(
                TagList(
                    tags.strong("Legal preparedness: "),
                    "To what extent are legal arrangements in place to respond effectively and "
                    "mitigate trade consequences?",
                )
            ),
        ),
        tags.p(
            "Trade vulnerability is considered from two complementary angles: a shock ",
            tags.strong("within the country"),
            " (domestic production and export-market access), and a shock ",
            tags.strong("in a trading partner"),
            " (especially a major supplier), disrupting imports. Economic sensitivity and legal "
            "preparedness therefore cover both export-side vulnerability after a domestic outbreak "
            "and import-side vulnerability from outbreaks in key supplying countries."
        ),
        tags.p(
            "This prototype focuses on ",
            tags.strong("foot-and-mouth disease (FMD)"),
            " and relies almost exclusively on existing datasets. Available data may not always "
            "match the ideal indicators for each dimension — especially legal preparedness, where "
            "internationally comparable structured data remain limited."
        ),
        tags.h3("Architecture (work in progress)"),
        tags.p(
            "At the highest level the Index is an overall assessment of vulnerability to the "
            "trade-related consequences of a specified animal disease. That score is built from "
            "the three dimensions above. Each dimension is assessed through indicators drawn from "
            "existing sources, converted where needed to comparable scores, then aggregated to a "
            "dimension score and into the overall Index."
        ),
        tags.p(
            "Relative weights for indicators and dimensions are still to be developed and tested. "
            "The intention is not only a headline number, but a transparent breakdown so users can "
            "see which factors drive a country’s profile and where remedies are most relevant. "
            "Guidance such as the OECD/JRC handbook on composite indicators (common scales, "
            "rationale for weights, sensitivity to alternative weighting) informs this work."
        ),
        tags.h3("Conceptual model in this prototype"),
        tags.p(
            "Disease Exposure and Economic Sensitivity increase vulnerability. Legal Preparedness "
            "is a resilience score: higher preparedness reduces vulnerability when combined into "
            "the Index."
        ),
    )
