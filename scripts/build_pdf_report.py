"""Create the publication-ready EXOhSPEC Th-Ar technical report PDF."""

from __future__ import annotations

import shutil
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "exohspec-thar-detector-study.pdf"
FIGURES = ROOT / "report" / "figures"

NAVY = colors.HexColor("#102f52")
INK = colors.HexColor("#142033")
MUTED = colors.HexColor("#536174")
BLUE = colors.HexColor("#1e5e91")
CYAN = colors.HexColor("#18a7b5")
ORANGE = colors.HexColor("#c56820")
RULE = colors.HexColor("#cbd3dc")
PALE = colors.HexColor("#edf4f7")
PAPER = colors.white


def _page(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - (11 if doc.page == 1 else 3.5) * mm, width, (11 if doc.page == 1 else 3.5) * mm, fill=1, stroke=0)
    canvas.setFillColor(ORANGE)
    canvas.rect(0, height - (12.2 if doc.page == 1 else 4.2) * mm, width, (1.2 if doc.page == 1 else 0.7) * mm, fill=1, stroke=0)
    canvas.setStrokeColor(RULE)
    canvas.line(18 * mm, 13 * mm, width - 18 * mm, 13 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 8.5 * mm, "Biswajit Jana | University of Hertfordshire")
    canvas.drawRightString(width - 18 * mm, 8.5 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle", parent=base["Title"], fontName="Times-Bold", fontSize=29,
            leading=31, textColor=NAVY, alignment=TA_LEFT, spaceAfter=8 * mm,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle", parent=base["Normal"], fontName="Helvetica", fontSize=11,
            leading=16, textColor=MUTED, spaceAfter=4 * mm,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName="Times-Bold", fontSize=20,
            leading=23, textColor=NAVY, spaceBefore=5 * mm, spaceAfter=3.2 * mm,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11.5,
            leading=14, textColor=BLUE, spaceBefore=3.5 * mm, spaceAfter=1.8 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Times-Roman", fontSize=9.35,
            leading=13.1, textColor=INK, spaceAfter=2.6 * mm,
        ),
        "small": ParagraphStyle(
            "Small", parent=base["BodyText"], fontName="Helvetica", fontSize=7.6,
            leading=10.4, textColor=MUTED, spaceAfter=1.8 * mm,
        ),
        "caption": ParagraphStyle(
            "Caption", parent=base["BodyText"], fontName="Helvetica", fontSize=7.4,
            leading=10, textColor=MUTED, spaceBefore=1.5 * mm, spaceAfter=3.5 * mm,
        ),
        "callout": ParagraphStyle(
            "Callout", parent=base["BodyText"], fontName="Helvetica", fontSize=9,
            leading=13, textColor=INK,
        ),
        "metric": ParagraphStyle(
            "Metric", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=16,
            leading=18, textColor=NAVY, alignment=TA_CENTER,
        ),
        "metric_label": ParagraphStyle(
            "MetricLabel", parent=base["BodyText"], fontName="Helvetica", fontSize=7,
            leading=9, textColor=MUTED, alignment=TA_CENTER,
        ),
        "ref": ParagraphStyle(
            "Reference", parent=base["BodyText"], fontName="Times-Roman", fontSize=8.1,
            leading=10.8, textColor=INK, leftIndent=4 * mm, firstLineIndent=-4 * mm,
            spaceAfter=1.8 * mm,
        ),
    }


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def _heading(number: str, title: str, styles: dict[str, ParagraphStyle]) -> list:
    return [Spacer(1, 1 * mm), _p(f'<font color="#c56820">{number}</font>  {title}', styles["h1"])]


def _figure(name: str, width_mm: float, height_mm: float, caption: str, styles: dict[str, ParagraphStyle]) -> list:
    path = FIGURES / name
    if not path.is_file():
        raise FileNotFoundError(path)
    image = Image(str(path), width=width_mm * mm, height=height_mm * mm, kind="proportional")
    image.hAlign = "CENTER"
    return [image, _p(caption, styles["caption"])]


def _bullet(text: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    style = ParagraphStyle(
        "BulletCopy", parent=styles["body"], leftIndent=5 * mm, firstLineIndent=-3.5 * mm,
        bulletIndent=0, spaceAfter=1.5 * mm,
    )
    return Paragraph(f"<b>-</b> {text}", style)


def build() -> Path:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = _styles()
    width, height = A4
    frame = Frame(18 * mm, 21 * mm, width - 36 * mm, height - 44 * mm, id="main")
    doc = BaseDocTemplate(
        str(OUTPUT), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=23 * mm, bottomMargin=21 * mm, title="Thorium-argon spectral lines: a scientific guide",
        author="Biswajit Jana", subject="Emission physics and a measured thorium-argon FITS example",
    )
    doc.addPageTemplates(PageTemplate(id="scientific", frames=[frame], onPage=_page))
    story: list = []

    story += [
        Spacer(1, 25 * mm),
        _p("TECHNICAL REPORT  /  DATA RELEASE 0.2  /  SEPTEMBER 2026", styles["small"]),
        _p("Thorium-argon spectral lines: emission physics and a measured example", styles["title"]),
        _p("An educational spectroscopy report using privacy-reviewed EXOhSPEC FITS data", styles["subtitle"]),
        Spacer(1, 5 * mm),
    ]
    author_table = Table(
        [[_p("AUTHOR", styles["small"]), _p("Biswajit Jana", styles["body"])],
         [_p("CONTEXT", styles["small"]), _p("Curiosity-led report from practical EXOhSPEC work", styles["body"])],
         [_p("AFFILIATION", styles["small"]), _p("University of Hertfordshire", styles["body"])],
         [_p("EXPOSURES", styles["small"]), _p("30, 60, 120, and 180 seconds", styles["body"])],
         [_p("PUBLIC SCOPE", styles["small"]), _p("Detector coordinates; raw FITS and optical details withheld", styles["body"])]],
        colWidths=[35 * mm, 126 * mm],
    )
    author_table.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 1.2, NAVY),
        ("LINEBELOW", (0, 0), (-1, -1), 0.35, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [author_table, Spacer(1, 10 * mm)]
    decision = Table([[_p(
        "<b>Central idea.</b> A thorium-argon lamp produces a dense emission-line spectrum: discrete atomic "
        "transitions create bright features that can serve as a wavelength ruler in astronomical spectroscopy.",
        styles["callout"]
    )]], colWidths=[161 * mm])
    decision.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE), ("BOX", (0, 0), (-1, -1), 1, CYAN),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story += [decision, Spacer(1, 12 * mm), _p(
        "This report distinguishes measured detector morphology from atomic interpretation. No wavelength or species labels are assigned before a validated order trace and dispersion solution.",
        styles["small"]
    ), PageBreak()]

    story += _heading("ABSTRACT", "Summary", styles)
    story += [_p(
        "Thorium-argon (Th-Ar) hollow-cathode lamps produce a dense forest of narrow emission features and are established wavelength references for astronomical spectrographs. During practical work on the EXOhSPEC project, several Th-Ar spectra were recorded. Their appearance prompted the questions developed here: what are the bright lines, how does the lamp produce them, how do emission and absorption differ, and why is the spectrum useful? The measured frames provide a real example while private technical details remain unpublished.", styles["body"]),
        _p(
        "The unsaturated integrated response follows exposure time with <i>R</i><super>2</super> = 0.999276 and a maximum fractional residual of 1.994%. Pixels at or above 60,000 ADU increase from 1 at 30 s to 121 at 180 s. Phase correlation gives a maximum translation estimate of 0.071 native pixel relative to 120 s under a translation-only model. The 120 s frame is therefore recommended when one exposure must represent the set, while an HDR estimator provides the clearest detector-space visualization.", styles["body"]),
        _p("Keywords: thorium-argon; hollow-cathode lamp; echelle spectroscopy; wavelength calibration; EXOhSPEC; CMOS; exposure optimization", styles["small"]),
        Spacer(1, 4 * mm)]
    metric_data = [
        [_p("120 s", styles["metric"]), _p("0.9993", styles["metric"]), _p("1.994%", styles["metric"]), _p("0.071 px", styles["metric"])],
        [_p("recommended single frame", styles["metric_label"]), _p("response R<super>2</super>", styles["metric_label"]), _p("largest fit residual", styles["metric_label"]), _p("largest estimated shift", styles["metric_label"])],
    ]
    metrics = Table(metric_data, colWidths=[40.25 * mm] * 4)
    metrics.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f7f9")),
        ("BOX", (0, 0), (-1, -1), 0.6, RULE), ("INNERGRID", (0, 0), (-1, -1), 0.4, RULE),
        ("TOPPADDING", (0, 0), (-1, 0), 9), ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
    ]))
    story += [metrics, Spacer(1, 5 * mm)]
    story += _heading("1", "Purpose, scope, and privacy boundary", styles)
    story += [_p(
        "The main goal is educational: explain what a Th-Ar source is, why its spectrum consists of emission lines, how thorium and argon contribute, where the materials occur, and how such lamps support astronomical spectroscopy. The supplied exposures are a practical example of how those ideas appear on a detector before wavelength calibration.", styles["body"]),
        _p(
        "This release identifies EXOhSPEC and a generic ZWO CMOS-family detector. It intentionally omits exact hardware configuration, optical prescriptions, laboratory layout, raw detector dimensions, full headers, file paths, and raw images. Public coordinates are normalized. This protects the laboratory while preserving the analysis logic and aggregate evidence.", styles["body"]),
        PageBreak()]

    story += _heading("2", "Emission, absorption, and the hollow-cathode source", styles)
    story += [_p(
        "A Th-Ar lamp is a hollow-cathode discharge source. Argon ions bombard a thorium-bearing cathode and sputter thorium into the discharge. Collisions excite neutral and ionized species. Radiative relaxation produces photons at discrete energies, creating narrow emission features.", styles["body"])]
    story += _figure(
        "concept-thar-lamp.png", 161, 88.3,
        "Figure 1. AI-generated conceptual illustration of a Th-Ar lamp feeding a generic spectrograph entrance. It is not a photograph, engineering drawing, or representation of the private EXOhSPEC laboratory.", styles,
    )
    story += [_p(
        "The fill gas allows a discharge to form at low pressure. Positive argon ions accelerate toward the cathode and transfer momentum to its surface, releasing thorium atoms by sputtering. Electrons and ions then excite and ionize both species. The visible output is therefore a mixture of neutral and ionized thorium and argon transitions.", styles["body"])]
    story += _figure(
        "concept-thar-emission-process.png", 161, 80.4,
        "Figure 2. AI-generated conceptual sequence of argon-ion bombardment, thorium sputtering, excitation, and discrete photon emission. The artwork is explanatory rather than a literal cross-section.", styles,
    )
    story += [PageBreak(), _p("2.1 Emission lines versus absorption lines", styles["h2"])]
    story += _figure(
        "emission-vs-absorption.png", 161, 99.5,
        "Figure 3. Conceptual distinction between emission peaks and absorption deficits. The wavelength values are illustrative and are not measured EXOhSPEC line assignments.", styles,
    )
    story += [_p(
        "An emission line is a positive peak because the source adds photons at a transition wavelength. An absorption line is a deficit below a continuum because intervening matter removes photons. The EXOhSPEC lamp frame contains emission-line images; a stellar spectrum commonly contains absorption structure.", styles["body"]),
        _p(
        "A transition from upper energy E_u to lower energy E_l emits a photon satisfying E_u - E_l = h nu = hc / lambda. Th I, Th II, and Th III denote neutral, singly ionized, and doubly ionized thorium; Ar I, Ar II, and Ar III use the same charge-state convention. Roman numerals do not describe brightness.", styles["body"]),
        _p(
        "The detector records each transition convolved with the spectrograph line-spread function and pixel response. A measured feature therefore has a centroid, width, integrated area, peak height, local background, and uncertainty. Blends, saturation, background gradients, and asymmetry can bias the centroid used for calibration.", styles["body"])]

    story += _heading("3", "Why thorium and argon are used", styles)
    story += [_p(
        "Thorium supplies a dense pattern of narrow transitions. NIST Standard Reference Database 161 contains reference wavelengths for more than 20,000 Th I, Th II, and Th III features together with argon line lists. The dominant terrestrial isotope is thorium-232, whose approximately 1.40 x 10<super>10</super> year half-life and dominance reduce isotopic complexity.", styles["body"]),
        _p(
        "Argon sustains the discharge and adds Ar I, Ar II, and Ar III features. Some carrier-gas lines are very strong. This is useful for acquisition but challenging for detector dynamic range: faint thorium structure may require an exposure that pushes bright cores toward the ceiling.", styles["body"]),
        _p(
        "USGS estimates about 10.5 mg kg<super>-1</super> thorium in upper continental crust. NOAA gives argon as about 0.934% by volume of dry air, dominated by argon-40. Abundance does not determine calibration quality; reference accuracy, line density, usable intensity, and stability do.", styles["body"]),
        PageBreak()]

    story += _heading("4", "Reading the measured EXOhSPEC detector frame", styles)
    story += [_p(
        "The supplied FITS exposure is a two-dimensional echellogram, not a finished one-dimensional plot. Dispersion acts along a traced order; cross-dispersion separates neighbouring orders. The landscape presentation below makes these two roles explicit while keeping the sign of increasing wavelength unassigned.", styles["body"])]
    story += _figure(
        "detector-orientation.png", 161, 87.6,
        "Figure 4. Zoomed-out, rotated measured detector format. The arrows show provisional dispersion and cross-dispersion directions. Rotation changes presentation only; the wavelength-increase direction requires calibration.", styles,
    )
    story += [_p(
        "The broad pale region is diffuse recorded illumination, not an identified atomic line. Possible contributors include scattered light, order wings, reflections, and a spatially varying background. A final extraction should fit a local two-dimensional inter-order background and propagate its uncertainty.", styles["body"]), PageBreak(), _p("4.1 Detector morphology in detail", styles["h2"]), _p(
        "An inverse-hyperbolic-sine display stretch reveals weak structure while retaining bright features. Quantitative calculations use linear detector values; the stretch affects appearance only.", styles["body"])]
    story += _figure(
        "annotated-detector-map.png", 125, 159,
        "Figure 5. Measured detector morphology with a reading guide. Bright compact features are emission-line images. Repeated loci are candidate echelle traces, but order numbering and wavelengths require calibration.", styles,
    )
    story += [PageBreak()]

    story += _heading("5", "Detector-domain methodology", styles)
    method_sections = [
        ("5.1 FITS ingestion", "The primary image is memory mapped and FITS scaling keywords are applied so calculations use physical unsigned detector values. Only exposure time is admitted to public metadata."),
        ("5.2 Robust background", "The pedestal is the median of a sparse full-frame sample. Scatter is 1.4826 times the median absolute deviation, which is resistant to sparse bright features."),
        ("5.3 Public crop", "Bright-pixel coordinate percentiles define a padded feature-rich region. Published axes are normalized and raw detector dimensions remain private."),
        ("5.4 Common mask", "The 180 s signal-rate image defines a source mask that is dilated to cover the local feature footprint. Linearity uses only pixels below 55,000 ADU in every exposure."),
        ("5.5 Response model", "Pedestal-subtracted counts in the common mask are summed and fitted through the origin against exposure time. This is an exposure-response diagnostic, not a complete camera-linearity calibration."),
        ("5.6 Registration", "Block-averaged log images are compared by phase correlation, with parabolic interpolation around the peak. The model fits translation only, not rotation, scale, or local distortion."),
        ("5.7 HDR estimator", "At each pixel, the longest exposure below 60,000 ADU is converted to signal per second. Shorter exposures replace longer values near the adopted ceiling."),
        ("5.8 Candidates", "Local maxima after mild Gaussian smoothing are ranked. The 500 displayed candidates are morphological detections and must not be interpreted as 500 identified atomic lines."),
    ]
    for heading, body in method_sections:
        story += [KeepTogether([_p(heading, styles["h2"]), _p(body, styles["body"])])]
    equation = Table([[_p(
        "<b>HDR rate estimator</b><br/>R(x,y) = [I<sub>t*</sub>(x,y) - B<sub>t*</sub>] / t*<br/>"
        "where t* is the longest exposure for which I<sub>t*</sub> is below 60,000 ADU.", styles["callout"]
    )]], colWidths=[161 * mm])
    equation.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE), ("LINEBEFORE", (0, 0), (0, -1), 3, CYAN),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [equation, PageBreak()]

    story += _heading("6", "Quantitative exposure results", styles)
    exposure_table = Table([
        [_p("Exposure", styles["small"]), _p("Background", styles["small"]), _p("Robust sigma", styles["small"]), _p("Bright pixels", styles["small"]), _p(">=60,000 ADU", styles["small"]), _p("Signal / 30 s", styles["small"])],
        ["30 s", "502", "2.965", "6,267", "1", "1.00000"],
        ["60 s", "504", "4.448", "10,906", "15", "1.97961"],
        ["120 s", "505", "4.448", "17,998", "75", "4.01202"],
        ["180 s", "508", "4.448", "26,132", "121", "5.84104"],
    ], colWidths=[22 * mm, 28 * mm, 27 * mm, 28 * mm, 29 * mm, 27 * mm])
    exposure_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 1), (-1, -1), 8.2),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"), ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f7f9")]),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [exposure_table, Spacer(1, 4 * mm), _p(
        "The background pedestal changes by only 6 ADU across the sequence. Visible structure increases with exposure, but the near-ceiling population rises from 1 to 121 pixels. The integrated values remain close to the ideal exposure ratios 1:2:4:6.", styles["body"])]
    story += _figure(
        "detector-diagnostics.png", 150, 112.5,
        "Figure 6. Detector pedestal, visible structure, near-ceiling population, and integrated unsaturated response. The common-mask response gives R<super>2</super> = 0.999276.", styles,
    )
    story += [PageBreak()]

    story += _heading("7", "Registration and profile structure", styles)
    story += [_p(
        "Translation estimates relative to the 120 s frame are (-0.070, -0.012), (-0.065, -0.017), (0, 0), and (-0.045, -0.019) pixels in (y, x) for 30, 60, 120, and 180 s. The maximum magnitude is 0.071 pixel. These values show consistency under the algorithm, not a full uncertainty budget.", styles["body"])]
    story += _figure(
        "registration-shifts.png", 150, 75.8,
        "Figure 7. Phase-correlation shifts relative to 120 s after four-pixel block averaging.", styles,
    )
    story += _figure(
        "representative-profiles.png", 161, 114.2,
        "Figure 8. Representative detector-space profiles with asinh-scaled intensity. The lower coordinate is measured detector position; the upper axis names the wavelength parameter, but its numerical values remain unsolved.", styles,
    )
    story += [PageBreak()]

    story += _heading("8", "Interpretation and exposure recommendation", styles)
    story += [_p(
        "The 120 s exposure is sufficient for a single public example and is the recommended single frame for this sequence. It reveals much more faint structure than 30 or 60 s while retaining more bright-core headroom than 180 s. This result is specific to the acquisition conditions and must not be treated as a universal EXOhSPEC setting.", styles["body"]),
        _p(
        "For HDR construction the 180 s frame supplies 66,279 valid source-mask pixels. The estimator falls back to 120 s for 49 pixels, 60 s for 57 pixels, and 30 s for 14 pixels. The small fallback population carries disproportionately important bright-core information.", styles["body"]),
        _p("Recommended acquisition practice", styles["h2"]),
        _bullet("Retain 120 s as the main exposure for this configuration.", styles),
        _bullet("Retain a 30 s exposure to protect the strongest feature cores.", styles),
        _bullet("Retain 180 s where faint-feature visibility is important.", styles),
        _bullet("Repeat each duration if temporal repeatability and random uncertainty are required.", styles),
        _bullet("Do not increase beyond 180 s before reviewing near-ceiling behaviour and line-core linearity.", styles),
        _bullet("Keep complete calibration metadata privately even when public derivatives omit it.", styles),
        Spacer(1, 3 * mm),
        _p(
        "The present four frames are enough for this detector-domain report. Additional repeated observations would be needed for cosmic-ray rejection, lamp warm-up characterization, drift versus time, or a statistically defensible repeatability error.", styles["body"]),
        PageBreak()]

    story += _heading("9", "Detector coordinate and wavelength", styles)
    story += [_p(
        "An echelle image is recorded in detector coordinates. Along a traced order, the physical coordinate can be written as lambda(x,m), where x is detector position and m is order number. Figure 8 therefore shows both the measured normalized position and the wavelength parameter. Numerical wavelength values are absent because the supplied FITS files do not contain a validated pixel-to-wavelength solution. The peaks and smaller fluctuations are genuine Python-derived detector profiles, not illustrative curves.", styles["body"]),
        _p(
        "NIST SRD 161 provides the physical reference wavelengths used in Th-Ar work, including more than 20,000 thorium entries across its constituent spectra. These data explain why Th-Ar is an exceptionally rich wavelength reference; they are cited here as atomic-data provenance rather than attached to uncalibrated detector peaks.", styles["body"]),
        PageBreak()]
    story += _heading("10", "Limitations", styles)
    limitations = [
        "Only one frame exists at each duration; fixed-exposure repeatability is unknown.",
        "The response fit assumes stable lamp output across the sequence.",
        "Registration models only global translation.",
        "The 60,000 ADU ceiling is an adopted diagnostic threshold, not an independently calibrated linearity limit.",
        "The public background treatment is simpler than a full local scattered-light model.",
        "Feature candidates are not atomic identifications.",
        "No claim is made about absolute flux, resolving power, line-spread function, or radial-velocity precision.",
    ]
    story += [_bullet(item, styles) for item in limitations]
    story += [PageBreak()]

    story += _heading("11", "Applications to astronomical spectroscopy", styles)
    applications = [
        ("Absolute wavelength calibration", "Reference wavelengths convert detector coordinates into a physical wavelength scale."),
        ("Instrument drift", "Repeated lamp frames monitor motion of the spectral format."),
        ("Radial velocity", "Reliable wavelength coordinates are essential before small stellar Doppler shifts are interpreted."),
        ("Extraction diagnostics", "The line-rich pattern tests trace, background, and order-extraction consistency."),
        ("Resolution and line shape", "Isolated unsaturated features can constrain widths, asymmetry, and focus variation."),
        ("Hybrid calibration", "Th-Ar absolute anchors may be paired with a Fabry-Perot etalon or laser-frequency comb."),
    ]
    app_data = [[_p("Application", styles["small"]), _p("Role of Th-Ar", styles["small"])]]
    app_data += [[_p(a, styles["h2"]), _p(b, styles["body"])] for a, b in applications]
    app_table = Table(app_data, colWidths=[49 * mm, 112 * mm], repeatRows=1)
    app_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f7f9")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [app_table, Spacer(1, 4 * mm), _p(
        "In exoplanet work the lamp does not detect a planet. It establishes the instrumental wavelength coordinate against which stellar motion or atmospheric structure can be measured. Calibration uncertainty propagates into the astrophysical result.", styles["body"])]

    story += _heading("12", "Conclusions", styles)
    story += [_p(
        "The supplied EXOhSPEC sequence is sufficient for a high-level scientific report. It demonstrates a dense emission-line field and quantitatively captures the exposure trade between faint-feature reach and bright-core headroom. Response is close to proportional over 30-180 s on the common unsaturated mask, and global registration is stable under the stated phase-correlation model.", styles["body"]),
        _p(
        "Use 120 s when only one frame can be shown, but retain the full exposure ladder for HDR display and protection of bright cores. Do not publish atomic labels or wavelengths until trace extraction, line matching, the dispersion solution, and residual validation are complete.", styles["body"]),
        PageBreak()]

    story += _heading("ACKNOWLEDGEMENTS", "Supervision and contribution", styles)
    story += [_p(
        "During practical laboratory work on the EXOhSPEC project, <b>Biswajit Jana</b> recorded several thorium-argon spectra and became interested in understanding what the bright lines represent, how they are produced, and why they are useful. That curiosity led to the analysis and educational report presented here. The author gratefully acknowledges <b>Prof. Hugh Jones</b> for supervision of the EXOhSPEC work and <b>Prof. Bill Martin</b> for guidance and supervision during the optics laboratory work at the University of Hertfordshire.", styles["body"]),
        _p(
        "The public release was prepared to communicate the scientific analysis while respecting the privacy of the detector configuration, optical design implementation, laboratory layout, FITS headers, and raw data.", styles["body"])]
    story += _heading("REFERENCES", "Scientific and data sources", styles)
    refs = [
        "1. Lhospice, E. et al. (2019). <i>EXOhSPEC folded design optimization and performance estimation</i>. Proceedings of SPIE. <link href='https://uhra.herts.ac.uk/id/eprint/14227/1/20190626_ProcSPIE_EXOhSPEC_V3.pdf' color='#1e5e91'>Public manuscript</link>.",
        "2. University of Hertfordshire. <link href='https://star.herts.ac.uk/exohspec/' color='#1e5e91'>EXOhSPEC project page</link>.",
        "3. Nave, G. et al. <i>Spectrum of Th-Ar Hollow Cathode Lamps</i>. NIST SRD 161, DOI 10.18434/T4S01V. <link href='https://www.nist.gov/pml/spectrum-th-ar-hollow-cathode-lamps' color='#1e5e91'>NIST database</link>.",
        "4. Redman, S. L., Nave, G., and Sansonetti, C. J. (2014). The Spectrum of Thorium from 250 nm to 5500 nm. <i>ApJS</i> 211(1). DOI 10.1088/0067-0049/211/1/4.",
        "5. Errmann, R. et al. (2020). HiFLEx: A Highly Flexible Package to Reduce Cross-dispersed Echelle Spectra. <i>PASP</i> 132, 064504. DOI 10.1088/1538-3873/ab8783.",
        "6. Lovis, C. and Pepe, F. (2007). A new list of thorium and argon spectral lines in the visible. <i>Astronomy and Astrophysics</i>.",
        "7. US Geological Survey. <link href='https://pubs.usgs.gov/sir/2017/5118/elements/Thorium/Th_txt.html' color='#1e5e91'>Thorium in the upper continental crust and soils</link>.",
        "8. NOAA National Weather Service. <link href='https://prod-01-alb-www-noaa.woc.noaa.gov/jetstream/atmosphere' color='#1e5e91'>Composition of the atmosphere</link>.",
        "9. Commission on Isotopic Abundances and Atomic Weights. <link href='https://ciaaw.org/thorium.htm' color='#1e5e91'>Thorium isotopic composition</link>.",
        "10. NIST. <link href='https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ascii=ascii&amp;ele=Ar' color='#1e5e91'>Atomic weights and isotopic compositions for argon</link>.",
        "11. ESO. <link href='https://www.eso.org/observing/dfo/quality/ESPRESSO/qc/waveThAr_qc1.html' color='#1e5e91'>ESPRESSO wavelength-calibration quality control</link>.",
    ]
    story += [_p(ref, styles["ref"]) for ref in refs]
    story += [Spacer(1, 5 * mm), _p(
        "Reference line databases provide the atomic-data provenance used in Th-Ar spectroscopy. Their existence does not by itself identify peaks in the present detector images.", styles["small"])]

    doc.build(story)
    shutil.copy2(OUTPUT, ROOT / "web" / OUTPUT.name)
    return OUTPUT


if __name__ == "__main__":
    print(build())
