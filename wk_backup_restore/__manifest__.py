# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Odoo Database Backup",
  "summary"              :  """Module provide feature to admin to take backups of his instance's database and later download them. Keywords: Odoo database backup | Backup Odoo instance | Download Odoo database backup | Odoo SaaS database backup feature | Automated Odoo backups | Odoo backup and restore | Secure Odoo database backup | Odoo SaaS Kit backup solution | Odoo cloud database backup | Backup and download Odoo database | Manage Database Backups""",  
  "category"             :  "Extra Tools",
  "version"              :  "1.0.4",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/",  
  "description"          :  """Module provide feature to admin to take backups of his instance's database and later download them.""",
  "live_test_url"        :  "http://odoodemo.webkul.com/demo_feedback?module=wk_backup_restore",  
  "depends"              :  [
                             'base',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'data/backup_process_sequence.xml',
                             'views/backup_process.xml',
                             'data/backup_ignite_crone.xml',
                             'views/menuitems.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "external_dependencies":  {'python': ['python-crontab']},
}
