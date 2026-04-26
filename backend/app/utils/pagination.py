from flask import request


def pagination_args(default_sort="-created_at"):
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 20)), 1), 100)
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", default_sort).strip()
    return page, per_page, search, sort


def paginate(query, schema, page, per_page):
    data = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": schema.dump(data.items, many=True),
        "page": data.page,
        "per_page": data.per_page,
        "total": data.total,
        "pages": data.pages,
    }
