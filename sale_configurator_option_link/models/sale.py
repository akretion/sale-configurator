# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

    
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    link_parent_option_id = fields.Many2one(
        "product.configurator.option",
        string="Link Parent Option",     
    )
    link_parent_sol_id = fields.Many2one(
        "sale.order.line",
        string="Link Parent Sale Order Line",
    )
    virtual_link_parent_sol_id = fields.Char(string="Virtual Link Parent ID", copy=False)
    virtual_new_id = fields.Char(string="Virtual New ID", copy=False)
    
    def _set_included_options(self):
        new_lines = self.env["sale.order.line"]
        
        for child_option_line in self.child_option_ids:
            child_option_line.virtual_new_id = str(child_option_line.id)
            included_line = self._create_new_included_option(child_option_line)
            if included_line:
                new_lines += included_line
                
        if new_lines:
            self.child_option_ids += new_lines
        return new_lines
    
    @api.onchange("child_option_ids")
    def _onchange_child_option_ids(self):
        if self.child_option_ids:
            current_option_ids = self.child_option_ids.mapped("option_id").ids
            if current_option_ids:
                parent_lines = self.child_option_ids.filtered(
                    lambda l: l.option_id.included_by_option_id and l.option_id.id in current_option_ids
                )
                included_options = parent_lines.mapped('option_id.included_by_option_id')
                child_lines_to_remove = self.child_option_ids.filtered(lambda l: l.option_id in included_options)
                
                if child_lines_to_remove:
                    self.child_option_ids -= child_lines_to_remove
                    
            self._set_included_options()
            self._action_resequence_options()
    
    def _create_new_included_option(self, child_option_line):
        opt_to_include = child_option_line.option_id.included_by_option_id
        
        if opt_to_include:
            proportional_qty = 1.0
            if opt_to_include.option_qty_type == "proportional_qty":
                proportional_qty = 1.0 * self.product_uom_qty
                
            vals = {
                "order_id": self.order_id.id or self._context.get('default_order_id'),
                "product_id": opt_to_include.product_id.id,
                "product_uom_qty": proportional_qty,
                "product_uom": opt_to_include.product_uom_id.id,
                "option_id": opt_to_include.id,
                "link_parent_option_id": child_option_line.option_id.id, 
                "link_parent_sol_id": child_option_line.id,
                "virtual_link_parent_sol_id": str(child_option_line.id),
            }
            return self.env["sale.order.line"].new(vals)
        return self.env["sale.order.line"]
    
    def _action_resequence_options(self):
        parents = self.child_option_ids.filtered(lambda l: not l.link_parent_sol_id and l.option_id)
        current_sequence = 10

        for parent in parents:
            parent.sequence = current_sequence
            children = self.child_option_ids.filtered(lambda l: l.link_parent_sol_id == parent)
            
            child_sequence = current_sequence + 1
            for child in children:
                child.sequence = child_sequence
                child_sequence += 1
                
            current_sequence += 10
            self.child_option_ids = self.child_option_ids.sorted(key=lambda l: l.sequence)
        return True
    
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._repair_option_links()
        return records
    
    def _repair_option_links(self):
        link_parent_lines = self.filtered(lambda l: l.virtual_new_id)
        link_child_lines = self.filtered(lambda l: l.virtual_link_parent_sol_id and not l.link_parent_sol_id)
        for line in link_child_lines:
            parent_line = link_parent_lines.filtered(lambda l: l.virtual_new_id == line.virtual_link_parent_sol_id)[0]
            if parent_line:
                line.update({
                    "link_parent_sol_id": parent_line.id,
                    "link_parent_option_id": parent_line.option_id.id,
                    "virtual_link_parent_sol_id": "",
                })
