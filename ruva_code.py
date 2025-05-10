import pickle
import pandas as pd
import wntr
import networkx as nx
import numpy as np
from datetime import datetime, timedelta
import psycopg2
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import sys
import os




table_name  = 'pressure'

def plot_interactive_network(network=None, longlat_map=None, link_attribute=None, node_attribute=None, crs="EPSG3857", node_attr_name = None, link_attr_name = None, filename='length.html', tiles = "OpenStreetMap", finder = False, zoom_start=15, add_to_link_popup = None,add_to_node_popup =None ):

    crs = crs or "EPSG3857"
     
    try:
        mp = None
        if not longlat_map:
            print(link_attribute)
            print(node_attribute)
        
            mp = wntr.graphics.plot_leaflet_network(network,
                                               link_attribute=link_attribute,
                                               link_width=3,
                                               node_size= 3,
                                               node_attribute=node_attribute, node_attribute_name =node_attr_name,
                                               link_attribute_name=link_attr_name,
                                               link_labels=True,
                                               zoom_start=zoom_start,
                                               filename=filename,
                                               add_legend=True, crs=crs,
                                               tiles = tiles, finder = finder,
                                               link_units=add_to_link_popup,
                                                node_units = add_to_node_popup,
                                               )
 


        message = "Successful"
        previous_map_locations = longlat_map

        
        return message, previous_map_locations, mp

    except Exception as e:
        print(f"the network  mapper failed serioulysy {e}")
        raise


class WaterNetworkGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Water Network Monitoring System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize water monitor with hardcoded credentials
        self.water_monitor = WaterMonitor(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres",
            password="hande22"
        )
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self.create_controls()
        self.create_map_display()
        self.water_monitor.monitored_atrr = self.metric_combo.currentText()
        self.load_network()
        self.handle_update()
    
    def create_controls(self):
        """Create control panel with metric selection and timer buttons"""
        control_layout = QHBoxLayout()
        self.metric_combo = QComboBox()
        self.metric_combo.addItems(['elevation',
            "Betweenness Centrality",
            "Node Degree",
            "Eccentricity", 'pressure', 'head', 
            'demand'
        ])
        self.metric_combo.currentTextChanged.connect(self.handle_update)
        control_layout.addWidget(QLabel("Select Metric:"))
        control_layout.addWidget(self.metric_combo)
        
        # Timer controls
        self.start_btn = QPushButton("Start Monitoring")
        self.start_btn.clicked.connect(self.start_monitoring)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Monitoring")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        control_layout.addWidget(self.stop_btn)
        
        self.layout.addLayout(control_layout)
    


    def create_map_display(self):
        self.browser = QWebEngineView()
        self.browser.setHtml("<h1>Water Network Visualization</h1><p>Select a metric and start monitoring</p>")
        self.layout.addWidget(self.browser)
    
    def load_network(self):
        try:
            if not os.path.exists('wn.pickle'):
                QMessageBox.critical(self, "Error", "Could not find wn.pickle file in current directory")
                return
            

            result = self.water_monitor.load_net('wn.pickle')
            if result != "success":
                QMessageBox.warning(self, "Network Error", "Could not load water network file (wn.pickle)")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load network: {str(e)}")
    
    def start_monitoring(self):
        selected_metric = self.metric_combo.currentText()
        self.water_monitor.monitored_atrr = selected_metric
        self.handle_update()
        

    def stop_monitoring(self):
        self.water_monitor.timer00.stop()

    def handle_update(self):
        global table_name
        selected_metric = self.metric_combo.currentText().replace(" ", "_").lower()
        self.water_monitor.monitored_atrr = self.metric_combo.currentText()
        if selected_metric in ['betweenness_centrality', 'node_degree', 'eccentricity', 'length','elevation']:
            self.water_monitor.metrics(selected_metric)
        else:
            table_name = selected_metric
            self.water_monitor.continuously_check()
            self.water_monitor.handle_update(restart = True)
        if self.water_monitor.html:
            self.browser.setHtml(self.water_monitor.html)















class WaterMonitor:
    def __init__(self, host, port, database, user, password):
        self.monitored_atrr = 'elevation'
        self.last_fetched_timestamp2 = '2000-01-01 00:00:00'
        self.generated_net = None
        self.results_link = {}
        self.results_node = {}
        self.schema_monitored = 'hob_infra'
        self.timer00 = QTimer()
        self.html = None
        self.cursorg_mr = None
        self.sensor_simulator = None
        

        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

       
        
        # Connect to database
        try:
            self.conng_mr = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursorg_mr = self.conng_mr.cursor()
            self.new_postgr_connected_mr = True
        except Exception as e:
            print(f"Database connection failed: {e}")
            self.new_postgr_connected_mr = False
        

        self.res_units = {
            'pressure': 'm',
            'head': 'm',
            'elevation': 'm',
            'demand': 'm3/s',
        }
      
        
        self.load_net()
        self.update_network_x_things()
        self.install_monitoring_system_toPostgr( self.schema_monitored, no_update = True)

    def start_auto_updates(self, check = False, restart = False):
        self.sensor_simulator_func(restart= restart)

    
   
    def stop_continuus_checks(self):  # create the button to stop the continus checks
        try:
            self.timer00.stop()
        except:
            pass 

    def continuously_check(self):  # creat a button to turn the continuous checking mode on
        if self.new_postgr_connected_mr:
            self.timer00.timeout.connect(self.handle_update)
            self.timer00.start(10000)
  
    def no_net(self):
        print("No network loaded, make sure you have a 'wn.pickle' file in your directory")


    
    def load_net(self, filename='wn.pickle', return_it = False):

        """
        Loads a saved network from a file.

        Args:
            filename (str): The filename to load the network from. Defaults to 'wn.pickle'.

        Returns:
            None
        """
        try:
            
            with open(filename, 'rb') as f:
                if return_it:
                    return pickle.load(f)
                self.generated_net = pickle.load(f)
                self.handle_update()
            return "success"
        except Exception as e:
            print(f"Error loading network: {e}")






    def display_folium_map(self, nodeattr = None, linkattr= None):
        if not self.generated_net:
            self.no_net()
            return
        print(nodeattr)
        print("laaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.monitoring_attribute = self.monitored_atrr
        try:

           
  
            add_to_node_popup = None
            add_to_link_popup = None

            
            
            if nodeattr is not None:
                add_to_node_popup = self.res_units.get(self.monitoring_attribute.lower(), '')
            

            
            msg = plot_interactive_network(network=self.generated_net, node_attribute=nodeattr,
                                                link_attribute=linkattr,
                                                link_attr_name=self.monitoring_attribute,
                                                node_attr_name=self.monitoring_attribute, add_to_node_popup = add_to_node_popup, add_to_link_popup= add_to_link_popup)

            message, _ , m = msg
            
            if message != "Successful":
                return

            
            self.html = m.get_root().render()
            
            
            # Make sure you use the above html to update your dashboard  or uncomment the part below if you want to save the hmtl and reload it in yoiur function
            #m.save('water_network_map.html')
         

        except Exception as e:
            print("failed to display folium error: (e)")
            print(e)

    def metrics(self, metric):
   
        try:
            series = None  # Will store the resulting Series
        
            if metric == 'betweenness_centrality':
                series = self.node_betweenness()
            elif metric == 'node_degree':
                series = self.node_degree()
            elif metric == 'eccentricity':
                series = self.calculate_diameter_and_eccentricity()
            elif metric =='length':
                series = self.generated_net.query_link_attribute("length")
            elif metric == 'elevation':
                series = self.generated_net.query_node_attribute("elevation")

          
            if series is not None and not series.empty:
         
                self.display_folium_map(series )
              
                
            else:
                print("The df is emopty")
                    
        except Exception as e:
            print(f"Error in metrics calculation: {e}")

    def node_betweenness(self) -> pd.Series:
        try:
            betweenness = nx.betweenness_centrality(self.G)
            return pd.Series(betweenness, name='Betweenness Centrality')
        except Exception as e:
            print(f"failed: ERROR: {e}")
            return pd.Series()  # Return empty Series on error

    def node_degree(self) -> pd.Series:
        try:
            node_degrees = dict(self.G.degree())
            return pd.Series(node_degrees, name='Degree')
        except Exception as e:
            print(f"failed: ERROR: {e}")
            return pd.Series()

    def calculate_diameter_and_eccentricity(self) -> pd.Series:
        try:
            if self.generated_net is None:
                self.no_net()
                return pd.Series()
            
            eccentricity = nx.eccentricity(self.uG)
            return pd.Series(eccentricity, name='Eccentricity')
        except Exception as e:
            print(f"failed: ERROR: {e}")
            return pd.Series()
    
    def update_network_x_things(self):
        try:
            if  self.generated_net is None:
                return
            self.G = self.generated_net.to_graph()  # directed multigraph
            self.uG = self.G.to_undirected()  # undirected multigraph
            self.sG = nx.Graph(self.uG)  # undirected simple graph (single edge between two nodes)
        except Exception as e:
            print(f"failed: eRROR: {e}")




    def install_monitoring_system_toPostgr(self, schema, no_update = False):
        """
        Install the water monitoring system in the database.
        """
        try:
            self.schema_monitored = schema
            self.cursorg_mr.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema_monitored};")

            # List of monitored attributes
            attributes = ['pressure', 'head', 'demand', 'velocity'
                          'flowrate'
                          ]

            for attribute in attributes:
                # Create the table for the attribute
                query = f"""
                CREATE TABLE IF NOT EXISTS {self.schema_monitored}.{attribute} (
                    timestamp TIMESTAMP PRIMARY KEY,
                    """

        
                names =  self.generated_net.junction_name_list # pipes
        

                for i in names:
                   query += f'"{i}" FLOAT,'
                query = query.rstrip(',')  # Remove the trailing comma
                query += ");"
                
                self.cursorg_mr.execute(query)

         

            self.conng_mr.commit()

            self.new_postgr_connected_mr = True


            if no_update:
                return

            self.handle_update()


        except Exception as e:
            print("failed error: ", e)
            return e
        
    





    

    def handle_update(self, restart = False):
        print("called")
        if self.monitored_atrr in ['Node Degree', 'Betweenness Centrality', 'Eccentricity', 'length','elevation',]:
            try:
              self.timer00.stop()
            except:
                pass
            self.metrics(self.monitored_atrr.replace(" ", "_").lower())
            return
        elif self.monitored_atrr in ['pressure', 'head',  'demand'
                          ]:
                  
            pass
        else:
            print(f"could not find :{self.monitored_atrr }")
            return
        self.start_auto_updates(check = True, restart = restart) # Ensure the updates are always running is always running
        print("the monitored attribute is : ",self.monitored_atrr )
        try:
            
            if self.last_fetched_timestamp2 is None:
                self.cursorg_mr.execute(f'SELECT * FROM {self.schema_monitored.lower().replace(" ","_")}.{self.monitored_atrr.lower().replace(" ","_")} '
                                        f"ORDER BY timestamp DESC "
                                        f"LIMIT 1")
            else:
                self.cursorg_mr.execute(f'SELECT * FROM {self.schema_monitored.lower().replace(" ","_")}.{self.monitored_atrr.lower().replace(" ","_")} '
                                        f"WHERE timestamp > %s "
                                        f"ORDER BY timestamp DESC "
                                        f"LIMIT 1", (self.last_fetched_timestamp2,))
            
            
            new_data = self.cursorg_mr.fetchone()
            #
           
            if new_data:
                print("thhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
                column_names = [desc[0] for desc in self.cursorg_mr.description]
                print(column_names)
                
       
                
                indexes = column_names[1:]
                values = new_data[1:]  # Exclude the first value (timestamp)
            
                series = pd.Series(data=values, index=indexes)
                print(series)

                
                self.display_folium_map(nodeattr = series)
         

                self.last_fetched_timestamp2 = new_data[0]
            else:
                print("no data found")
             

       


        except Exception as e:
            self.timer00.stop()
            print(e)
         





    def add_network_for_monitoring(self):
        if not self.new_postgr_connected_mr:
            print( "You must establish a connection before proceeding.")
            return
        network_name = self.monitored_atrr
        if network_name and network_name != "":
            try:
                
                user_schemag = network_name.strip().replace(" ", "_") + "_water_monitor"
                self.install_monitoring_system_toPostgr(user_schemag)   

            except Exception as e:
                print(e)
                return
  
    







    def sensor_simulator_func(self, check  = False, restart = False):
            if not self.generated_net:
                return
            if not self.schema_monitored:
                print("No schema selected. To get started, create an example schema by specifying a name")

                return
 
           
            self.install_monitoring_system_toPostgr(self.schema_monitored, no_update = True)
            avg_value = 1
            
  
   


            if not self.sensor_simulator:
                self.sensor_simulator = SensorSimulator(self.schema_monitored, self.host, self.port, self.database, self.user, self.password, self.monitored_atrr.lower().replace(" ", "_"), passed_value= avg_value)   
                self.sensor_simulator.show()
                self.sensor_simulator.connect()
                self.sensor_simulator.simulate_sensor_updates()
                if self.sensor_simulator.isVisible():
                    print("sensor updator visible")
              
            elif restart:
                if self.sensor_simulator:
                   self.sensor_simulator.stop_simulation()
                self.sensor_simulator = SensorSimulator(self.schema_monitored, self.host, self.port, self.database, self.user, self.password, self.monitored_atrr.lower().replace(" ", "_"), passed_value= avg_value)   
                self.sensor_simulator.show()
                self.sensor_simulator.connect()
                self.sensor_simulator.simulate_sensor_updates()


          












class SensorSimulator(QDialog):
    def __init__(self, schema, host, port, database, user, password, table_name, passed_value = 1):
        super().__init__()
        self.schema_prefix = schema
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.table_name = table_name
        self.conn = None
        self.cursor = None
        self.stop_simulation_flag = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.column_names = None
        self.color_index = 0
        self.passed_value = passed_value
        self.standard_deviation = passed_value*0.1
      
        self.move(0, 0)
        self.setStyleSheet('background-color: black; color: cyan')
        
        self.label = QPushButton("Inserting Data Into The Database.. (Click To Stop)")
        self.label.setFont(QFont("Arial", 20))
        self.label.setStyleSheet("background-color: rgb(64, 0, 64); color: cyan")
        self.label.clicked.connect(self.stop_simulation)

        self.colors = [QColor('cyan'), QColor('yellow'), QColor('green')]


        # Create a layout and add the label
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)



    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()
        except (Exception, psycopg2.Error) as error:
            print(f"Error connecting to PostgreSQL: {error}")

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def get_column_names(self):
        query = f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = '{self.schema_prefix}' 
            AND table_name = '{table_name}'
        """
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return [row[0] for row in result]
        except Exception as e:
            return []

    def get_max_timestamp(self):
        if not hasattr(self, 'column_names') or not self.column_names:
            self.column_names = self.get_column_names()
        if not self.column_names:
           self.stop_simulation()
           QMessageBox.information(self, 'No names found', f'No names (columns) found in the {table_name} table of the schema {self.schema_prefix}.')
           self.close()
           return
        
        query = f"SELECT MAX({self.column_names[0]}) FROM {self.schema_prefix}.{table_name}"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result[0]

    def simulate_sensor_updates(self):
        self.stop_simulation_flag = False
        self.column_names = self.get_column_names()
        self.max_timestamp = self.get_max_timestamp()
        if self.max_timestamp is None:
            self.max_timestamp = datetime.now()
        else:
            self.max_timestamp += timedelta(hours=1)
        self.timer.start(500)  # 1000 milliseconds = 1 second

    def update_simulation(self):
        try:
            #print(f"inserting data hey schema is {self.schema_prefix }")
            if self.stop_simulation_flag:
                self.timer.stop()
                return
            # Generate random values for the devices
            device_values = np.random.normal(loc=self.passed_value, scale=self.standard_deviation, size=len(self.column_names) - 1)


            # Insert the data into the database
            columns = ', '.join([f'"{col}"' for col in self.column_names])
            placeholders = ', '.join(['%s'] * len(self.column_names))
            query = f"""
                INSERT INTO {self.schema_prefix}.{table_name} 
                ( {columns} ) 
                VALUES ( {placeholders} )
            """
            values = [self.max_timestamp] + list(device_values)

            print(values)
           
            self.cursor.execute(query, values)
            self.conn.commit()
            # Increment the timestamp by 1 second
            self.max_timestamp += timedelta(seconds=1)
            self.update_label_color()
        except Exception as e:
            self.stop_simulation()
            print(e)

    

    def update_label_color(self):
        self.color_index = (self.color_index + 1) % len(self.colors)
        self.label.setStyleSheet(f"background-color: rgb(64, 0, 64); color: {self.colors[self.color_index].name()}")




    def stop_simulation(self):
        self.stop_simulation_flag = True
        self.disconnect()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Skip login dialog and go straight to main window with hardcoded credentials
    try:
        main_window = WaterNetworkGUI()
        main_window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)














