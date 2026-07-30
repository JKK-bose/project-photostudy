from graphviz import Digraph

g = Digraph('ER', format='png')
g.attr(rankdir='LR', bgcolor='white', fontname='Segoe UI')
g.attr('node', shape='none', fontname='Segoe UI', fontsize='11')

def entity(name, title, fields):
    rows = "".join(
        f'<TR><TD ALIGN="LEFT" BGCOLOR="{"#FFF3E0" if pk else "white"}">{icon} {fname}</TD>'
        f'<TD ALIGN="LEFT">{ftype}</TD></TR>'
        for fname, ftype, pk, icon in fields
    )
    label = f'''<
    <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6">
    <TR><TD COLSPAN="2" BGCOLOR="#FF7A45"><FONT COLOR="white"><B>{title}</B></FONT></TD></TR>
    {rows}
    </TABLE>>'''
    g.node(name, label=label)

entity('users', 'users (Пользователи)', [
    ('id', 'INT, PK', True, '&#128273;'),
    ('full_name', 'VARCHAR(150)', False, ''),
    ('login', 'VARCHAR(50), UNIQUE', False, ''),
    ('password_hash', 'VARCHAR(255)', False, ''),
    ('phone', 'VARCHAR(20)', False, ''),
    ('email', 'VARCHAR(100)', False, ''),
    ('role', "ENUM('client','admin')", False, ''),
    ('created_at', 'DATETIME', False, ''),
])

entity('photoshoot_types', 'photoshoot_types (Варианты фотосессий)', [
    ('id', 'INT, PK', True, '&#128273;'),
    ('name', 'VARCHAR(100)', False, ''),
    ('description', 'TEXT', False, ''),
    ('price', 'DECIMAL(10,2)', False, ''),
    ('duration_minutes', 'INT', False, ''),
])

entity('bookings', 'bookings (Заявки на фотосессию)', [
    ('id', 'INT, PK', True, '&#128273;'),
    ('user_id', 'INT, FK', False, '&#128279;'),
    ('photoshoot_type_id', 'INT, FK', False, '&#128279;'),
    ('booking_date', 'DATE', False, ''),
    ('booking_time', 'TIME', False, ''),
    ('payment_method', "ENUM('cash','card','online')", False, ''),
    ('status', "ENUM('new','confirmed','completed','cancelled')", False, ''),
    ('comment', 'TEXT', False, ''),
    ('created_at', 'DATETIME', False, ''),
])

g.edge('users', 'bookings', label='1 : N  (user_id)', fontname='Segoe UI', fontsize='10')
g.edge('photoshoot_types', 'bookings', label='1 : N  (photoshoot_type_id)', fontname='Segoe UI', fontsize='10')

g.render('/sessions/dazzling-dreamy-gates/mnt/outputs/project/docs/er_diagram', cleanup=True)
print("done")
