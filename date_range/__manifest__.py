
{
    "name": "Plage de Dates",
    "summary": "Manage all kind of date range",
    "version": "14",
    "category": "Uncategorized",
    "author": "BMG Tech",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "web",
    ],
    # odoo_test_helper is needed for the tests
    "data": [
        "data/ir_cron_data.xml",
        "security/ir.model.access.csv",
        "security/date_range_security.xml",
        "views/assets.xml",
        "views/date_range_view.xml",
        "wizard/date_range_generator.xml",
    ],
    "qweb": ["static/src/xml/date_range.xml"],
    "development_status": "Mature",
    "maintainers": ["lmignon"],
}
