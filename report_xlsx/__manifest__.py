
{
    "name": "Base report xlsx",
    "summary": "Base module to create xlsx report",
    "author": "BMG Tech",
    "website": "",
    "category": "Reporting",
    "version": "14",
    "license": "AGPL-3",
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "depends": ["base", "web"],
    "data": ["views/webclient_templates.xml"],
    "demo": ["demo/report.xml"],
    "installable": True,
}
