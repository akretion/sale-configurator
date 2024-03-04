def migrate(cr, version):
    # As we do not know how the sol was created we need to set them configured by default
    cr.execute(
        """UPDATE sale_order_line SET is_configured=true WHERE is_configured IS NULL"""
    )
