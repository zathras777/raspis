import math

def make_gallery(photos, width = 920, size = 'Medium', max_pics = 0, max_rows = 0):
    gallery = {'rows': [], 'qty': 0}
    row = { 'images': [], 'height': 0 }
    w = 0
    for p in photos:
        i = p.get_thumbnail(size)
        if row['height'] == 0 or row['height'] > i.img.height:
            row['height'] = i.img.height
        
        if w < width:
            row['images'].append(i)
            w += i.img.width + 6
            continue
        else:
            row['width'] = w
            gallery['rows'].append(row)
            w = i.img.width + 6
            row = { 'images': [i], 'height': i.img.height }

    if len(row['images']):
        row['width'] = w
        gallery['rows'].append(row)
        
    for r in gallery['rows']:
        r['data'] = []
        if r['width'] <= width:
            for i in r['images']:
                r['data'].append({'url': i.img.url, 'width': i.img.width, 
                                  'diff': 0, 'id': i.photo.id})
        else:
            diff = r['width'] - width
            new_width = 0
            for i in r['images']:
                iw = float(i.img.width + 6)
                dw = math.ceil((iw / r['width']) * diff)
                if new_width + dw > diff:
                    dw = diff - new_width
                new_width += dw
                r['data'].append({'url': i.img.url, 
                                  'diff': math.ceil(dw / 2), 
                                  'hdiff': math.ceil((i.img.height - r['height']) / 2),
                                  'width': i.img.width - dw,
                                  'id': i.photo.id})
            r['width'] = width
        gallery['qty'] += len(r['data'])

    return gallery

