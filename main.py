from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from random import randint, choice
from sqlalchemy import func

#API
import requests

headers = {
    'Authorization' : 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImM5MTAxMmYwLTIwMjctNGI4Ny1iYjJhLTIwMWFjZWM4ZjM0OCIsImlhdCI6MTc0NzIxNjIxNiwic3ViIjoiZGV2ZWxvcGVyL2FjYjY1ZDI4LWY5NDctZjZjZC0xZTdlLWZlNzRiZGM0M2I4NSIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjg1LjIzOS4xMDIuMTEzIl0sInR5cGUiOiJjbGllbnQifV19.8BUCboH8-dDyN2EV0izuMmjkjFYygDFV5xua0GaFKBxb-Cv8epMf1Puf2NZkK9QO_Xi5SqgNyCVZNxBFQs3iEg'
}

def calcProz(lista):
    max = 0
    user = 0
    for i in lista:
        max += i.get('maxLevel', 0)
        user += i.get('level', 0)
    if user == 0 or max == 0:
        result = 0
    else:
        result = round((user / max) * 100, 1)
    return result

def get_user(playerID):
    response = requests.get('https://api.clashofclans.com/v1/players/%23' + playerID, headers=headers)
    if response.status_code == 200:
        user_json = response.json()

        troops_list = user_json.get('troops', [])
        pet_names = {
            'l.a.s.s.i',
            'mighty yak',
            'electro owl',
            'unicorn',
            'phoenix',
            'poison lizard',
            'diggy',
            'frosty',
            'spirit fox',
            'angry jelly',
        }
        builder_base_names = {
            'raged barbarian',
            'sneaky archer',
            'boxer giant',
            'beta minion',
            'bomber',
            'baby dragon',
            'cannon cart',
            'night witch',
            'drop ship',
            'power p.e.k.k.a',
            'hog glider',
            'electrofire wizard',
        }

        pets = []
        builder_base_troops = []
        normal_troops = []

        count = 0
        for troop in troops_list:
            name_lower = troop.get('name', '').lower().strip()

            if name_lower in pet_names:
                pets.append(troop)
            elif name_lower in builder_base_names:
                if name_lower == 'baby dragon'  and count == 0:
                    normal_troops.append(troop)
                    count += 1
                else:
                    builder_base_troops.append(troop)
            else:
                normal_troops.append(troop)
        exclude_names = ['super', 'sneaky goblin', 'rocket', 'inferno', 'ice hound']
        troops = [
            troop for troop in normal_troops
            if all(exclude_name not in troop.get('name', '').lower() for exclude_name in exclude_names)
        ]

        heroes_list = user_json.get('heroes', [])
        sorted_heroes = sorted(heroes_list, key=lambda hero: hero.get('village', '').lower() == 'builderbase')
        builder_base_heroes = sorted_heroes[-2:]
        heroes = sorted_heroes[:-2]
        
        player_stats = {
            'tag': user_json.get('tag'),
            'name': user_json.get('name'),
            'townHallLevel': user_json.get('townHallLevel'),
            'expLevel': user_json.get('expLevel'),
            'trophies': user_json.get('trophies'),
            'bestTrophies': user_json.get('bestTrophies'),
            'builderHallLevel': user_json.get('builderHallLevel'),
            'builderBaseTrophies': user_json.get('builderBaseTrophies'),
            'bestBuilderBaseTrophies': user_json.get('bestBuilderBaseTrophies'),
            'clan': {
                'name': user_json['clan']['name'] if 'clan' in user_json else None,
                'tag': user_json['clan']['tag'] if 'clan' in user_json else None
            },
            'league': {
                'name': user_json['league']['name'] if 'league' in user_json else None,
                'iconUrls': user_json['league']['iconUrls'] if 'league' in user_json else None
            },
            'builderBaseLeague': {
                'name': user_json['builderBaseLeague']['name'] if 'builderBaseLeague' in user_json else None
            },
            'troops': troops,
            'builder_troops': builder_base_troops,
            'pets': pets,
            'heroes': heroes,
            'builder_heroes': builder_base_heroes,
            'heroEquipment': user_json.get('heroEquipment', []),
            'spells': user_json.get('spells', []),
            'prozentHero': calcProz(heroes),
            'prozentTroop': calcProz(troops),
            'prozentPet': calcProz(pets),
            'prozentSpell': calcProz(user_json.get('spells', [])),
            'prozentEquipment': calcProz(user_json.get('heroEquipment', [])),
            'prozentBuilderHero': calcProz(builder_base_heroes),
            'prozentBuilderTroop': calcProz(builder_base_troops)
        }
        return player_stats
    else:
        print(f"Fehler beim Abrufen der Daten: {response.status_code}")
        return None

#api

#APP DB
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///numberbank.db'
app.config['SQLALCHEMY_BINDS'] = {
    'numberbank': 'sqlite:///numberbank.db',
    'operatorbank': 'sqlite:///operatorbank.db' ,
    'playerbank': 'sqlite:///playerbank.db',
    'playerstatsbank': 'sqlite:///playerstatsbank.db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
#app db

symbol = ["+", "-", "*", "//"]

class Message(db.Model):
    __tablename__ = "Message"
    __bind_key__ = 'numberbank'
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(200), nullable = True)
    content = db.Column(db.Integer, nullable = False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

class Operator(db.Model):
    __tablename__ = "Operator"
    __bind_key__ = 'operatorbank'
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(10), nullable = False)

class Player(db.Model):
    __tablename__ = "Player"
    __bind_key__ = 'playerbank'
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(30), nullable = True)
    playertag = db.Column(db.String(8), nullable = False)

#1 zu n relation 2x (PlayerBuilding ist Mittler zwischen Player und BuildingType)
class PlayerStats(db.Model):
    __tablename__ = "PlayerStats"
    __bind_key__ = 'playerstatsbank'
    id = db.Column(db.Integer, primary_key = True)
    playertag = db.Column(db.String(8), nullable = False)
    buildings = db.relationship('PlayerBuilding', backref='player', lazy=True, cascade="all, delete-orphan") #löscht alle Gebäude des Spielers bei Löschung des Spielers

class BuildingType(db.Model):
    __tablename__ = "BuildingType"
    __bind_key__ = 'playerstatsbank'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False, unique = True)
    max_level = db.Column(db.Integer, nullable = False)
    max_count = db.Column(db.Integer, nullable = True)
    buildings = db.relationship('PlayerBuilding', backref='building_type', lazy=True)

class PlayerBuilding(db.Model):
    __tablename__ = "PlayerBuilding"
    __bind_key__ = 'playerstatsbank'
    id = db.Column(db.Integer, primary_key = True)
    player_id = db.Column(db.Integer, db.ForeignKey('PlayerStats.id', ondelete='CASCADE'), nullable = False) #cascade delete 
    building_type_id = db.Column(db.Integer, db.ForeignKey('BuildingType.id'), nullable = False)
    level = db.Column(db.Integer, nullable = False)
    position = db.Column(db.Integer, nullable = False)
    
    __table_args__ = (
        db.UniqueConstraint('player_id', 'building_type_id', 'position', name='unique_building_position'), #keine doppelten Gebäude an der selben Position
    )

def default_add(first):
    if first:
        new_message = Message(
            user = "vlado",
            content = 1
        )
    else:
        new_message = Message(
            user = "vlado",
            content = request.form['content']
        )
    db.session.add(new_message)
    db.session.commit()

    new_message = Message(
        user = "Bot",
        content = randint(1,99)
    )
    db.session.add(new_message)
    db.session.commit()

    rsymbol = choice(symbol)
    new_operator = Operator(
        content = rsymbol
    )
    db.session.add(new_operator)
    db.session.commit()

@app.route("/", methods=['GET', 'POST'])
def start_page():
    return render_template('index.html')

@app.route("/game", methods=['GET', 'POST'])  #<name>
def game_page(): #name
    if request.method == 'POST' and "content" in request.form:

        lastnum2 = Message.query.order_by(Message.id.desc()).limit(2)
        for last in lastnum2:
            usernum = last.content
        lastnum = Message.query.order_by(Message.id.desc()).limit(1)
        for last in lastnum:
            botnum = last.content
        lastop = Operator.query.order_by(Operator.id.desc()).limit(1)
        for last in lastop:
            operator = last.content
        lastopid = Operator.query.order_by(Operator.id.desc()).limit(2)
        for last in lastopid:
            opid = last.content
        
        answer = eval(str(usernum) + str(operator) + str(botnum))
        print(answer)
        
        if request.form['content'] == str(answer):
            default_add(False)

    if request.method == 'POST' and "reset" in request.form:
        db.session.query(Message).delete()
        db.session.query(Operator).delete()
        db.session.commit()
        default_add(True)

    messages = Message.query.order_by(Message.created_at).all()
    operations = Operator.query.order_by(Operator.id).all()
    return render_template('game.html', messages=messages, operations = operations)

@app.route("/cocplayer", methods=['GET', 'POST'])
def cocplayer_page():
    if request.method == 'POST':
        if "playertag" in request.form and "user_input" not in request.form and "delete_player" not in request.form and "track_player" not in request.form:
            playertag_to_add = request.form['playertag']
            existing_player = Player.query.filter_by(playertag=playertag_to_add).first()
            if not existing_player:
                if get_user(playertag_to_add) != None:
                    new_player = Player(
                        nickname = "",
                        playertag = request.form['playertag']
                    )
                    new_player_stats = PlayerStats(
                        playertag = request.form['playertag']
                    )

                    db.session.add(new_player)
                    db.session.add(new_player_stats)
                    db.session.commit()
    
        if "user_input" in request.form and "playertag" in request.form:
            user_input = request.form['user_input']
            print(user_input)
            playertag_to_update = request.form['playertag']
            print(playertag_to_update)
            player_to_update = Player.query.filter_by(playertag=playertag_to_update).first()
            if player_to_update:
                player_to_update.nickname = user_input
                db.session.commit()
        
        if "delete_player" in request.form:
            playertag_to_delete = request.form['playertag']
            player_to_delete = Player.query.filter_by(playertag=playertag_to_delete).first()
            player_stats_to_delete = PlayerStats.query.filter_by(playertag=playertag_to_delete).first()
            if player_to_delete:
                db.session.delete(player_to_delete)
                db.session.commit()
            if player_stats_to_delete:
                db.session.delete(player_stats_to_delete)
                db.session.commit()

    players = Player.query.order_by(Player.id).all()
    return render_template('cocplayer.html', players = players)

@app.route("/coc", methods=['GET', 'POST'])
def coc_page():
    player_stats = None
    if request.method == 'GET':
        playertag = request.args.get('playertag')
        player_stats = get_user(playertag)

    return render_template('coc.html', player_stats = player_stats)

#////////////

@app.route("/cocbuildings", methods=['GET'])
def coc_buildings_page():
    player_stats = None
    if request.method == 'GET':
        playertag = request.args.get('playertag')
        player_stats = get_user(playertag)
    player = PlayerStats.query.filter_by(playertag=playertag).first()
    player_buildings = PlayerBuilding.query.filter_by(player_id=player.id).all()
    available_building_types = BuildingType.query.all()
    return render_template('coc_buildings.html', player_stats=player_stats,player_buildings=player_buildings,available_building_types=available_building_types)

@app.route("/update_building_level", methods=['POST'])
def update_building_level():
    data = request.get_json()
    building_id = data.get('building_id')
    change = data.get('change')
    
    if not building_id or not change:
        return jsonify({'success': False, 'message': 'Ungültige Anfrage'})
    
    building = PlayerBuilding.query.get(building_id)
    if not building:
        return jsonify({'success': False, 'message': 'Gebäude nicht gefunden'})
    
    new_level = building.level + change
    if new_level < 1 or new_level > building.building_type.max_level:
        return jsonify({'success': False, 'message': 'Ungültiges Level'})
    
    building.level = new_level
    db.session.commit()
    
    return jsonify({'success': True})

@app.route("/add_building", methods=['POST'])
def add_building():
    data = request.get_json()
    try:
        building_type_id = int(data.get('building_type_id'))
        level = int(data.get('level'))
    except Exception as e:
        return jsonify({'success': False, 'message': 'Ungültige Datentypen'})
    playertag = request.args.get('playertag')

    if playertag == 'PGUV0R0Q':
        playertag = playertag.replace('0', 'O')
    for p in PlayerStats.query.all():
        print(f"DB-Tag: '{p.playertag}' | HEX: {[hex(ord(c)) for c in p.playertag]}")
    print(f"Request-Tag: '{playertag}' | HEX: {[hex(ord(c)) for c in playertag]}")
    normalized_tag = playertag.lower().strip()
    player = PlayerStats.query.filter(func.lower(func.trim(PlayerStats.playertag)) == normalized_tag).first()
    if not player:
        return jsonify({'success': False, 'message': 'Spieler nicht gefunden'})
    building_type = BuildingType.query.get(building_type_id)
    if not building_type:
        return jsonify({'success': False, 'message': 'Gebäudetyp nicht gefunden'})
    if level < 1 or level > building_type.max_level:
        return jsonify({'success': False, 'message': 'Ungültiges Level'})
    existing_buildings = PlayerBuilding.query.filter_by(player_id=player.id, building_type_id=building_type_id).order_by(PlayerBuilding.position).all()
    used_positions = {b.position for b in existing_buildings}
    position = 1
    while position in used_positions:
        position += 1
    if building_type.max_count is not None and len(existing_buildings) >= building_type.max_count:
        return jsonify({'success': False, 'message': f'Maximale Anzahl ({building_type.max_count}) für {building_type.name} erreicht'})
    existing_building = PlayerBuilding.query.filter_by(
        player_id=player.id,
        building_type_id=building_type_id,
        position=position
    ).first()
    if existing_building:
        return jsonify({'success': False, 'message': 'Gebäude an dieser Position existiert bereits'})
    try:
        new_building = PlayerBuilding(
            player_id=player.id,
            building_type_id=building_type_id,
            position=position,
            level=level
        )
        db.session.add(new_building)
        db.session.commit()
        return jsonify({
            'success': True,
            'building': {
                'id': new_building.id,
                'name': building_type.name,
                'level': new_building.level,
                'position': new_building.position,
                'max_level': building_type.max_level
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Fehler beim Speichern: {str(e)}'})

@app.route("/delete_building", methods=['POST'])
def delete_building():
    data = request.get_json()
    building_id = data.get('building_id')
    if not building_id:
        return jsonify({'success': False, 'message': 'Ungültige Anfrage'})
    building = PlayerBuilding.query.get(building_id)
    if not building:
        return jsonify({'success': False, 'message': 'Gebäude nicht gefunden'})
    player_id = building.player_id
    building_type_id = building.building_type_id
    try:
        db.session.delete(building)
        db.session.commit()
        buildings = PlayerBuilding.query.filter_by(player_id=player_id, building_type_id=building_type_id).order_by(PlayerBuilding.position).all()
        for idx, b in enumerate(buildings, start=1):
            b.position = idx
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Fehler beim Löschen: {str(e)}'})

def init_building_types():
    building_types = [
        {"name": "Air Defense", "max_level": 15, "max_count": 4},
        {"name": "Archer Tower", "max_level": 21, "max_count": 8},
        {"name": "Cannon", "max_level": 21, "max_count": 7},
        {"name": "Wizard Tower", "max_level": 17, "max_count": 5},
        {"name": "Mortar", "max_level": 17, "max_count": 4},
        {"name": "Air Sweeper", "max_level": 7, "max_count": 2},
        {"name": "Hidden Tesla", "max_level": 15, "max_count": 5},
        {"name": "Bomb Tower", "max_level": 12, "max_count": 2},
        {"name": "X-Bow", "max_level": 12, "max_count": 4},
        {"name": "Inferno Tower", "max_level": 11, "max_count": 3},
        {"name": "Eagle Artillery", "max_level": 7, "max_count": 1},
        {"name": "Scattershot", "max_level": 6, "max_count": 2},
        {"name": "Monolith", "max_level": 4, "max_count": 1},
        {"name": "Spell Tower", "max_level": 3, "max_count": 2},
        {"name": "Multi-Archer Tower", "max_level": 3, "max_count": 2},
        {"name": "Ricochet-Cannon", "max_level": 3, "max_count": 2},
        {"name": "Builder Hut", "max_level": 7, "max_count": 5},
    ]
    
    for building in building_types:
        if not BuildingType.query.filter_by(name=building["name"]).first():
            new_type = BuildingType(
                name=building["name"],
                max_level=building["max_level"],
                max_count=building.get("max_count")
            )
            db.session.add(new_type)
    db.session.commit()

@app.route("/auto_add_buildings", methods=['POST'])
def auto_add_buildings():
    playertag = request.args.get('playertag')
    if not playertag:
        return jsonify({'success': False, 'message': 'Kein Playertag angegeben'})

    if playertag == 'PGUV0R0Q':
        playertag = playertag.replace('0', 'O')
    normalized_tag = playertag.lower().strip()
    player = PlayerStats.query.filter(func.lower(func.trim(PlayerStats.playertag)) == normalized_tag).first()
    if not player:
        return jsonify({'success': False, 'message': 'Spieler nicht gefunden'})
    building_types = BuildingType.query.all()
    added = 0
    for btype in building_types:
        if btype.max_count is None:
            continue
        existing = PlayerBuilding.query.filter_by(player_id=player.id, building_type_id=btype.id).count()
        to_add = btype.max_count - existing
        for i in range(to_add):
            used_positions = {b.position for b in PlayerBuilding.query.filter_by(player_id=player.id, building_type_id=btype.id).all()}
            position = 1
            while position in used_positions:
                position += 1
            new_building = PlayerBuilding(
                player_id=player.id,
                building_type_id=btype.id,
                position=position,
                level=1
            )
            db.session.add(new_building)
            added += 1
    db.session.commit()
    return jsonify({'success': True, 'added': added})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        init_building_types()
    app.run(debug=True)
    #get_user("PGUVOROQ")