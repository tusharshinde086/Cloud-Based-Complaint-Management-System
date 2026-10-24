from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_GET
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

from complaint_accounts.models import UserProfile
from complaint_records.models import Complaint


def _role(user):
    if user.is_superuser or user.is_staff:
        return "Admin"
    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return "User"


def _visible_complaints(user):
    qs = Complaint.objects.select_related("created_by", "assigned_to").all()
    role = _role(user)
    if role == "Admin":
        return qs
    if role == "Staff":
        return qs.filter(assigned_to=user)
    return qs.filter(created_by=user)


def _filtered_complaints(request):
    qs = _visible_complaints(request.user)
    status = request.GET.get("status", "").strip()
    category = request.GET.get("category", "").strip()
    start = parse_date(request.GET.get("start_date", ""))
    end = parse_date(request.GET.get("end_date", ""))
    if status:
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category=category)
    if start:
        qs = qs.filter(created_at__date__gte=start)
    if end:
        qs = qs.filter(created_at__date__lte=end)
    return qs.order_by("-created_at")


@login_required
@require_GET
def complaint_report_pdf(request):
    complaints = _filtered_complaints(request)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="complaint_report.pdf"'

    document = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="Complaint Management Report",
        author="Cloud-Based Complaint Management System",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], alignment=TA_CENTER, fontSize=16,
        leading=20, spaceAfter=6
    )
    small_style = ParagraphStyle(
        "SmallCell", parent=styles["BodyText"], fontSize=7, leading=9, spaceAfter=0
    )
    story = [
        Paragraph("Complaint Management Report", title_style),
        Paragraph(
            f"Generated: {timezone.localtime(timezone.now()).strftime('%d %b %Y, %I:%M %p')}",
            styles["Normal"],
        ),
        Paragraph(f"Records included: {complaints.count()}", styles["Normal"]),
        Spacer(1, 8),
    ]

    headers = ["Complaint ID", "Title", "Category", "Priority", "Status",
               "Created By", "Assigned To", "Created"]
    data = [headers]
    for complaint in complaints:
        data.append([
            Paragraph(str(complaint.complaint_id or ""), small_style),
            Paragraph(str(complaint.title or ""), small_style),
            Paragraph(str(complaint.category or ""), small_style),
            Paragraph(str(complaint.priority or ""), small_style),
            Paragraph(str(complaint.status or "").replace("_", " "), small_style),
            Paragraph(str(complaint.created_by.get_username() if complaint.created_by else ""), small_style),
            Paragraph(str(complaint.assigned_to.get_username() if complaint.assigned_to else "Unassigned"), small_style),
            Paragraph(timezone.localtime(complaint.created_at).strftime("%d-%b-%Y") if complaint.created_at else "", small_style),
        ])

    widths = [27*mm, 53*mm, 27*mm, 20*mm, 25*mm, 31*mm, 31*mm, 25*mm]
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243b53")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd2d9")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f6f9")]),
    ]))
    story.append(table)

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#52606d"))
        canvas.drawRightString(landscape(A4)[0] - 12*mm, 7*mm, f"Page {doc.page}")
        canvas.restoreState()

    document.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return response
