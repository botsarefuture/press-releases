# views.py
from flask import (
    Blueprint,
    session,
    redirect,
    url_for,
    render_template,
    request,
    abort,
    send_from_directory,
    Response,
)
import xml.etree.ElementTree as ET
from flask_login import login_required
from db import PressReleaseDatabase

# Create a Blueprint for the main routes
main = Blueprint("main", __name__)

# Initialize the database
PRDB = PressReleaseDatabase()


@main.route("/")
def index():
    """
    Home page displaying a list of press releases.
    """
    press_releases = PRDB.get_press_releases()
    for item in press_releases:
        item["review"] = str(item.get("content", ""))[:50]
    return render_template("index.html", press_releases=press_releases)


@main.route("/releases/<id>")
def release(id: str):
    """
    Page to display a single press release.
    """
    release = PRDB.get_press_release(id)
    if not release:
        abort(404, description="Press release not found")
    return render_template("release.html", release=release)


@main.route("/new_release/", methods=["GET", "POST"])
@login_required
def new():
    """
    Page to create a new press release.
    """
    if request.method == "POST":
        print(request.form.to_dict())
        title = request.form.get("title")
        content = request.form.get("content")
        organization = request.form.get("organization")
        contact_name = request.form.get("contact_name")
        contact_email = request.form.get("contact_email")
        contact_phone = request.form.get("contact_phone")
        status = request.form.get("status")

        # Save the press release to the database
        PRDB.save_press_release(
            {
                "title": title,
                "content": content,
                "organization": organization,
                "contact_name": contact_name,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "status": status,
            }
        )

        return redirect(url_for("main.index"))

    return render_template("create_release.html")


@main.route("/static/<path:filename>")
def static_files(filename):
    """
    Serve static files from the 'static' directory.
    """
    return send_from_directory("static", filename)


@main.route("/sitemap.xml")
def sitemap():
    """
    Generate and serve the XML sitemap.
    """
    urls = [
        {"loc": url_for("main.index", _external=True), "lastmod": ""},
        {"loc": url_for("main.login_v2", _external=True), "lastmod": ""},
        {"loc": url_for("main.new", _external=True), "lastmod": ""},
    ]

    # Add press release URLs
    press_releases = PRDB.get_press_releases()
    for release in press_releases:
        urls.append(
            {
                "loc": url_for("main.release", id=release["_id"], _external=True),
                "lastmod": "",
            }
        )

    # Generate the XML
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for url in urls:
        url_elem = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_elem, "loc")
        loc.text = url["loc"]
        if url["lastmod"]:
            lastmod = ET.SubElement(url_elem, "lastmod")
            lastmod.text = url["lastmod"]

    sitemap_xml = ET.tostring(urlset, encoding="unicode", method="xml")

    return Response(sitemap_xml, mimetype="application/xml")
