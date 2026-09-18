"""Methodology content for Economic Sensitivity — concept + data-source options."""

from __future__ import annotations

from htmltools import HTML, TagList, tags

from src.ui.methodology_common import model_questions_block, source_card


def economic_methodology_section() -> TagList:
    """Colleague concept note + candidate data sources for team decision."""
    return TagList(
        tags.h3("Economic Sensitivity — methodology concept"),
        tags.p(
            "The economic sensitivity dimension assesses how strongly an animal-health shock "
            "could affect a country’s economy, livestock sector and associated livelihoods. "
            "It considers both losses arising from a domestic outbreak and disruption caused "
            "by outbreaks in key trading partners."
        ),
        tags.p("For the FMD prototype, this dimension will explore three components:"),
        tags.ul(
            tags.li(
                TagList(
                    tags.strong("Economic dependence and production at risk: "),
                    "Agriculture’s share of national GDP will provide context, while livestock’s "
                    "contribution to agricultural and national GDP will indicate more specific "
                    "economic dependence. The share of livestock production value attributable "
                    "to FMD-susceptible species will help identify the activities potentially at "
                    "risk. Where data permit, indicators will also consider vulnerability to "
                    "reduced productivity, mortality and disease-control costs.",
                )
            ),
            tags.li(
                TagList(
                    tags.strong("Export-side sensitivity: "),
                    "The importance of exports of susceptible livestock and their products "
                    "relative to domestic production, together with concentration in a small "
                    "number of destination markets, will indicate vulnerability to market-access "
                    "restrictions following a domestic outbreak.",
                )
            ),
            tags.li(
                TagList(
                    tags.strong("Import-side sensitivity: "),
                    "Reliance on imported livestock and animal products, concentration among "
                    "supplying countries, and the availability of alternative suppliers will "
                    "indicate vulnerability to outbreaks in trading partners, including potential "
                    "effects on food availability and prices.",
                )
            ),
        ),
        tags.p(
            "The prototype will draw on existing production, economic and trade datasets, "
            "including FAOSTAT, national accounts and UN Comtrade, subject to availability and "
            "comparability. Indicators will provide proxies for economic sensitivity rather than "
            "precise forecasts of outbreak losses. Selection and aggregation will seek to avoid "
            "double-counting closely related measures."
        ),
        tags.p(
            "Where relevant and supported by data, complementary indicators will explore food "
            "security, animal welfare, gender differences in livelihood impacts, greenhouse-gas "
            "emissions intensity, and antimicrobial use and associated AMR risks. These broader "
            "effects will initially be presented alongside the core economic score, recognising "
            "that their relevance and measurability will vary across diseases and countries."
        ),
        tags.div(
            {"class": "tvi-callout"},
            HTML(
                "<strong>Current prototype status:</strong> Economic Sensitivity in the live app "
                "is still a <strong>mock module</strong> (replaceable). FAOSTAT and UN Comtrade "
                "are listed here as primary candidates (moved from Disease Exposure, where they "
                "are better suited to production-at-risk and trade sensitivity). Disease Exposure "
                "may <em>reuse</em> the same bilateral trade matrices for RMT connection strength "
                "without scoring them twice in the TVI."
            ),
        ),
        tags.h3("Economic Sensitivity data sources — options for team decision"),
        tags.p(
            "FAOSTAT, national accounts and UN Comtrade are proposed as the core statistical "
            "backbone. Complementary indicators stay alongside the core score unless colleagues "
            "agree otherwise. Avoid double-counting closely related GDP, production and trade shares."
        ),
        tags.div(
            {"class": "tvi-source-grid"},
            source_card(
                "FAOSTAT (FAO)",
                "MAIN SOURCE — Production at risk & livestock dependence",
                "Wide country coverage of livestock populations, production quantities and "
                "values, and related agri-food series. Quality, timeliness and species detail "
                "vary; informal production is under-captured in some regions.",
                "Open bulk downloads and API; cache annual tables by country and FMD-susceptible "
                "species (cattle, buffalo, sheep, goats, pigs, etc.). No live call required once "
                "Parquet/CSV is built.",
                "Core inputs for economic dependence and production at risk: livestock output "
                "value, share of susceptible species, and production baselines used with trade "
                "ratios for export/import intensity.",
                "Implement first for the FMD prototype: build a cached FAOSTAT extract and "
                "derive standardised 0–100 sub-indicators (livestock economic importance; "
                "susceptible-species share). Share livestock stock figures with Disease Exposure "
                "only as optional pathway/host context — do not add a second weighted copy into TVI.",
                primary=True,
            ),
            source_card(
                "National accounts / World Bank & similar (agriculture & GDP structure)",
                "MAIN SOURCE — Macro dependence context",
                "Near-global coverage of GDP and sector value-added (agriculture, forestry and "
                "fishing). Livestock-specific GDP is often not published separately and may need "
                "approximation from FAOSTAT or national sources.",
                "World Bank Open Data / national statistical offices — CSV/API downloads; cache "
                "locally. Cross-check definitions (e.g. agriculture share vs livestock-only).",
                "Agriculture (and where possible livestock) share of GDP as context for how "
                "strongly a shock could transmit to the national economy.",
                "Use agriculture value-added % of GDP as a contextual or lightly weighted "
                "dependence indicator; prefer livestock-specific shares when available to avoid "
                "inflating sensitivity for crop-heavy economies.",
                primary=True,
            ),
            source_card(
                "UN Comtrade / livestock & animal-product trade statistics",
                "MAIN SOURCE — Export- and import-side sensitivity",
                "Near-global merchandise trade reporting for livestock and product HS codes; "
                "lags, confidentiality suppressions and informal/cross-border trade gaps apply.",
                "UN Comtrade API / bulk downloads; cache annual (then optional monthly) bilateral "
                "matrices for FMD-relevant HS chapters (live animals, meat, dairy, etc.).",
                "Export dependence (exports vs domestic production), destination concentration, "
                "import dependence, supplier concentration and alternative-supplier flexibility. "
                "Same bilateral matrices can feed Disease Exposure RMT “country-to-country "
                "connections” without a second TVI weight.",
                "Build one curated Comtrade cache for the project. Score Economic Sensitivity "
                "export/import components from it; allow Disease Exposure to reuse connection "
                "strength for pathways. Document HS code lists and concentration metrics (e.g. HHI).",
                primary=True,
            ),
            source_card(
                "ITC Trade Map / MACMap or equivalent trade intelligence (optional)",
                "Enhancement — Market access & tariff/NTM context",
                "Useful detail on partners and measures; licensing and coverage differ from "
                "Comtrade; risk of overlapping the same trade flows.",
                "Often licensed or portal export; prefer open Comtrade first.",
                "Refine interpretation of export-market vulnerability (e.g. dependence on "
                "high-barrier destinations) — not a replacement for Comtrade volumes.",
                "Only add if Comtrade alone is insufficient for the demo narrative; keep "
                "outside the core weighted score unless unique non-volume information is used.",
            ),
            source_card(
                "FAO / WFP / national food-security indicators",
                "Complementary — Food security (alongside core score)",
                "Global and national food-security metrics exist but are heterogeneous and not "
                "livestock-trade specific; relevance of an FMD shock to food security varies widely.",
                "Open FAO/WFP datasets where licence allows; manual selection of a small indicator set.",
                "Present beside the core Economic Sensitivity score to show livelihood/food "
                "availability stakes — not as a forecast of outbreak losses.",
                "Keep as a complementary panel in Country profile for v1; do not fold into the "
                "0–100 economic composite until colleagues agree disease-specific relevance.",
            ),
            source_card(
                "Gender & livelihood statistics (FAO / ILO / national)",
                "Complementary — Differentiated livelihood impacts",
                "Partial coverage; livestock-gender linkages are often survey-based and not "
                "annually updated for all countries.",
                "Mostly manual or curated extracts from FAO gender/livestock briefs and labour data.",
                "Flag where women’s/men’s livelihoods may be differentially exposed — narrative "
                "and optional side indicator.",
                "Display alongside core score for selected demo countries first; global scoring "
                "only if a comparable series can be defined.",
            ),
            source_card(
                "FAOSTAT emissions / livestock GHG intensity",
                "Complementary — Environmental co-effects",
                "FAOSTAT emissions series available for many countries; intensity metrics need "
                "careful normalisation and are not direct economic sensitivity.",
                "FAOSTAT open downloads; cache with production tables.",
                "Illustrate GHG co-benefits/risks of herd or trade disruption — alongside, not inside, "
                "the core economic score.",
                "Optional side chart in Country profile; exclude from weighted Economic Sensitivity "
                "unless the team explicitly expands the dimension’s scope.",
            ),
            source_card(
                "WOAH ANIMUSE / antimicrobial use & AMR-related data",
                "Complementary — AMU / AMR risks",
                "Improving but incomplete country reporting; not designed as an outbreak-loss model.",
                "WOAH ANIMUSE portal / published aggregates; check reuse terms; often manual.",
                "Context for disease-control cost/AMR pathways that may accompany intensive "
                "response — complementary to core economic sensitivity.",
                "Keep alongside the core score; do not use as a substitute for production or trade indicators.",
            ),
            source_card(
                "Animal welfare indicators (WOAH standards uptake / national metrics)",
                "Complementary — Welfare co-effects",
                "Few globally comparable quantitative welfare datasets; largely qualitative or "
                "standard-uptake proxies.",
                "Mostly manual / Observatory or national reports.",
                "Acknowledge welfare stakes of an FMD shock or control measures beside the "
                "economic score.",
                "Methodology note + optional qualitative flag for demo countries; not a v1 "
                "numeric input to the composite.",
            ),
        ),
        model_questions_block(
            "Questions for colleagues — Economic Sensitivity mathematical model",
            "Please answer these so we can replace the mock module with transparent formulas "
            "for dependence, export-side and import-side sensitivity (and optional complements).",
            [
                "What exact indicators enter each of the three components (dependence/production "
                "at risk; export-side; import-side), and what are the component weights that sum "
                "to the Economic Sensitivity Index?",
                "Which FMD-susceptible species and product categories are in scope, and which "
                "FAOSTAT series + UN Comtrade HS codes define them?",
                "How should “livestock contribution to GDP” be measured when livestock GDP is "
                "not published (FAOSTAT value shares, agriculture VA only, national estimates)?",
                "Export-side: should sensitivity use exports/production, exports/GDP, or both? "
                "How is destination concentration defined (top-1 / top-3 share, HHI) and weighted?",
                "Import-side: how do we score import reliance, supplier concentration, and "
                "availability of alternative suppliers (herfindahl, number of partners above a "
                "threshold, diversification index)?",
                "What reference year(s) or multi-year averages (e.g. 3-year mean) should we use "
                "to reduce volatility in trade and production series?",
                "Normalisation: min–max by global distribution, fixed expert thresholds, or "
                "percentile ranks? Same rule for all sub-indicators?",
                "Double-counting: which pairs of indicators must not both receive full weight "
                "(e.g. agriculture % GDP and livestock production value)?",
                "Domestic outbreak vs partner outbreak: do export-side and import-side already "
                "capture this split, or do we need an explicit scenario weight between them?",
                "Missing data: if Comtrade or FAOSTAT is missing for a country, Economic "
                "Sensitivity = N/A, partial score among available components, or regional proxy?",
                "Complementary indicators (food security, gender, GHG, AMU/AMR, welfare): confirm "
                "they stay outside the 0–100 composite for v1; if any should enter, with what weight?",
                "Should Disease Exposure reuse Comtrade matrices with zero additional TVI weight "
                "(recommended), or should connection strength also appear inside Economic Sensitivity?",
            ],
        ),
        tags.h3("Suggested decision path for Economic Sensitivity"),
        tags.ol(
            tags.li(
                TagList(
                    tags.strong("Confirm the three components"),
                    " (dependence/production at risk; export-side; import-side) and explicit "
                    "rules to avoid double-counting GDP, production and trade shares.",
                )
            ),
            tags.li(
                TagList(
                    tags.strong("Implement FAOSTAT + national accounts + UN Comtrade"),
                    " as the core statistical stack; replace the mock Economic Sensitivity module.",
                )
            ),
            tags.li(
                TagList(
                    "Agree HS codes and species lists for FMD-susceptible trade/production, "
                    "plus concentration metrics (e.g. top-partner share or HHI).",
                )
            ),
            tags.li(
                TagList(
                    "Allow Disease Exposure to ",
                    tags.strong("reuse"),
                    " Comtrade bilateral intensities for RMT connections — one cache, two uses, "
                    "one TVI weight (economic only).",
                )
            ),
            tags.li(
                "Keep food security, gender, GHG, AMU/AMR and welfare as complementary "
                "side indicators unless colleagues promote any into the weighted score."
            ),
        ),
    )
