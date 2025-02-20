
{
    "name": "MuK Backend Theme", 
    "summary": "Odoo Community Backend Theme",
    "version": "14",
    "category": "Themes/Backend", 
    "license": "LGPL-3", 
    "author": "BMG Tech",
    "depends": [
        "web_editor",
    ],
    "excludes": [
        "web_enterprise",
    ],
    "data": [
        "template/assets.xml",
        "template/web.xml",
        "views/res_users.xml",
        "views/res_config_settings_view.xml",
        "data/res_company.xml",
    ],
    "qweb": [
        "static/src/components/control_panel.xml",
        "static/src/xml/*.xml",
    ],
    "images": [
        'static/description/banner.png',
    ],
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
    "uninstall_hook": "_uninstall_reset_changes",
}
