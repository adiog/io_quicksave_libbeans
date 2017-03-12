def sql_order(bean_name, bean_spec):
    bean_id = bean_name + '_id'
    bean_hash = bean_name + '_hash'

    fields = sorted(bean_spec)

    if bean_id in bean_spec:
        fields.remove(bean_id)
        return bean_id, fields
    elif bean_hash in bean_spec:
        fields.remove(bean_hash)
        return bean_hash, fields
    else:
        return None, fields
