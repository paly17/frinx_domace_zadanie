import json
import psycopg2

# connect to database
conn = psycopg2.connect(
    host='localhost',
    database='postgres',
    user='postgres',
    password='postgres'
)
cursor = conn.cursor()

# delete all rows from table interface
cursor.execute(
    "DELETE FROM interface;"
)

# read json file
json_file = open('configClear_v2.json', 'r')
json_data = json_file.read()

# parse data from json file
parsed_data = json.loads(json_data)

interface_group_names = ['Port-channel', 'TenGigabitEthernet', 'GigabitEthernet']

# loop to iterate over all interfaces of type port-channel, TenGigabitEthernet and GigabitEthernet
for interface_group_name in interface_group_names:
    for element in parsed_data['frinx-uniconfig-topology:configuration']['Cisco-IOS-XE-native:native']['interface'][interface_group_name]:

        # write the data we want about each interface to variables
        if 'name' in element:
            name = interface_group_name + str(element['name'])
        else:
            name = None
        if 'description' in element:
            description = element['description']
        else:
            description = None
        if 'mtu' in element:
            max_frame_size = int(element['mtu'])
        else:
            max_frame_size = None

        if 'Cisco-IOS-XE-ethernet:channel-group' in element:
            port_channel_number = element['Cisco-IOS-XE-ethernet:channel-group']['number']
            port_channel_id = None
            sql = "SELECT * FROM interface WHERE name = %s;"
            val = ('Port-channel' + str(port_channel_number),)
            cursor.execute(sql, val)
            port_channel = cursor.fetchall()
            if port_channel:
                port_channel_id = port_channel[0][0]
        else:
            port_channel_id = None
        config = json.dumps(element)

        # insert data stored in variables into database
        sql = "INSERT INTO interface (name, description, config, port_channel_id, max_frame_size) VALUES (%s, %s, %s, %s, %s);"
        val = (name, description, config, port_channel_id, max_frame_size)
        cursor.execute(sql, val)
        conn.commit()

# close connection
cursor.close()
conn.close()
