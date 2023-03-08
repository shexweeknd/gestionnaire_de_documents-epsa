import sys 
import time
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget, QHeaderView, QSplashScreen
import sqlite3
import os

class Fenetre0(QSplashScreen):
    def __init__(self, retrieved_champs, retrieved_tables):
        super(Fenetre0, self).__init__()
        loadUi("UI/Fenetre0.ui",self)
        swidget.setFixedHeight(720)
        swidget.setFixedWidth(1280)
        #self.setWindowFlag(Qt.FramelessWindowHint)
        self.rc = retrieved_champs
        self.rt = retrieved_tables
        swidget.addWidget(self)
        print("c'est loadé")

    def func_ouvrir(self):
        time.sleep(2)
        self.fenetre1 = Fenetre1(self)
        swidget.addWidget(self.fenetre1)
        print(swidget.currentIndex())
        swidget.setCurrentWidget(self.fenetre1)

    def loading(self):
        swidget.show()
        time.sleep(2)
        self.func_ouvrir()

class Fenetre1(QDialog):
    def __init__(self, parent0):
        super(Fenetre1, self).__init__()
        loadUi("UI/Fenetre1.ui",self)
        self.constinit = True
        self.parent0 = parent0
        self.tables_list = []

        """actions avec bouttons etc ..."""

        #bouttons
        self.sauvegarder.clicked.connect(self.ecrire)
        self.nouveau.clicked.connect(self.nouveau_db)
        self.retirer.clicked.connect(self.delete)
        self.ouvrir.clicked.connect(self.ouvrir_db)
        self.ajouter.clicked.connect(self.ajouter_ligne)
        self.addTable.clicked.connect(self.add_table)
        self.removeTable.clicked.connect(self.rem_table)
        self.box.currentIndexChanged.connect(self.update_table)
        self.box.currentTextChanged.connect(self.activateAddTable)
        self.box.textHighlighted.connect(self.changeUI)
        self.filterBox.setEnabled(False)
        self.filterBox.setChecked(False)
        self.sauvegarder.setEnabled(False)
        self.addTable.setEnabled(False)
        self.removeTable.setEnabled(False)
        self.champderecherche.textChanged.connect(self.recherche)
        self.filterBox.stateChanged.connect(self.switch_mod)

    def initTableWidget(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setStyleSheet("background-color:rgb(255, 255, 255);")
        self.tableWidget.clear()
        self.tableWidget.setColumnWidth(0,250)
        self.tableWidget.setColumnWidth(1,100)
        self.tableWidget.setColumnWidth(2,350)

    def update_table(self, value):
        try:
            self.choosenTable = self.tables_list[value]
        except:
            self.choosenTable = self.parent0.rt[value]

    def changeUI(self, signal):
        
        print("le signal est: ", signal)
        print("le fichier est :", self.fichier)
        df = []

        conn = sqlite3.connect(self.fichier)
        cur = conn.cursor()
        try:
            for row in cur.execute(f"SELECT * FROM {signal}"):
                df.append(row)
            print(df)
            nblign = len(df)
            nbcol = len(df[0])

            #capture des champs de la table
            champs = []
            cur.execute(f"SELECT * FROM {signal}")
            for i, j in enumerate(list(cur.description)):
                champs.append(cur.description[i][0])

            #creation d'une table temporaire de recherche
            self.tableWidget.clear()
            self.tableWidget.setRowCount(nblign)
            self.tableWidget.setColumnCount(nbcol)
            #print("les champs sont :", champs)
            self.tableWidget.setHorizontalHeaderLabels(champs)
            self.tableWidget.horizontalHeader().setStretchLastSection(True)

            for lign, c in enumerate(df):
                for col, item in enumerate(c) :
                    i = QTableWidgetItem(item)
                    self.tableWidget.setItem(lign, col, i)

            vidange_Layout(self)
            self.gridLayout.addWidget(self.tableWidget)
        except: 
            print("classeur VIDE !!")
            #capture des champs de la table
            champs = []
            cur.execute(f"SELECT * FROM {signal}")
            for i, j in enumerate(list(cur.description)):
                champs.append(cur.description[i][0])
            print(champs)

            self.tableWidget.clear()
            self.tableWidget.setColumnCount(len(champs))
            self.tableWidget.setHorizontalHeaderLabels(champs)
            self.tableWidget.setRowCount(1)
            self.tableWidget.horizontalHeader().setStretchLastSection(True)
            vidange_Layout(self)
            self.gridLayout.addWidget(self.tableWidget)

    def switch_mod(self, value):
        if value == 0:
            #print("signal : ", value)
            #print("le texte du box actuel :", self.box.currentText())
            self.charger()
            self.recherche(self.champderecherche.text())

            self.warninglabel.setText("MESSAGE: Vous pouvez editer la table actuelle")
            self.champderecherche.textChanged.disconnect(self.filtrage)
            self.champderecherche.textChanged.connect(self.recherche)
            self.box.setEnabled(True)
            self.sauvegarder.setEnabled(True)
        elif value == 2:
            self.filtrage(self.champderecherche.text())

            self.warninglabel.setText("MESSAGE: Attention le mode filtré ne supporte pas de modification")
            self.champderecherche.textChanged.disconnect(self.recherche)
            self.champderecherche.textChanged.connect(self.filtrage)
            self.box.setEnabled(False)
            self.sauvegarder.setEnabled(False)


    """FONCTIONS BOUTTONS"""
    def nouveau_db(self):
        #ajouter une  nouvelle table avec des champs avec sqlquery)
        self.widget = QtWidgets.QStackedWidget()
        Fenetre2(self)

    def activateAddTable(self, signal):
        self.filterBox.setEnabled(True)
        self.addTable.setEnabled(True)
        self.removeTable.setEnabled(True)
        if signal == "" or signal == None:
            self.addTable.setEnabled(False)
            self.removeTable.setEnabled(False)
    
    def fillWidget(self, signal):
        print(self.fichier)
        
        vidange_Layout(self)
        self.initTableWidget()
        self.gridLayout.addWidget(self.tableWidget)
        #recuperation des données dans un tuple
        print(self.fichier)
        try :
            self.connection = sqlite3.connect(self.fichier)
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            self.tables = self.cursor.fetchall()

            self.tables_list = []
            for t in self.tables:
                self.tables_list.append(t[0])
            
            #ajout du choix de table
            self.choosenTable = signal
            print(self.fichier)
            
            df = []
            listrow = 0
            for row in self.cursor.execute("SELECT * FROM "+str(self.choosenTable)):
                listrow += 1
                df.append(list(row))
            

            self.tableWidget.setRowCount(len(df))

            #capture des champs de la table
            self.champs = []
            for i, j in enumerate(list(self.cursor.description)):
                self.champs.append(self.cursor.description[i][0])
            
            #ajout des champs dans les headers
            self.tableWidget.setColumnCount(len(self.champs))
            self.tableWidget.setHorizontalHeaderLabels(self.champs)
            self.tableWidget.horizontalHeader().setStretchLastSection(True)
        
        except:
            pass
        
        if self.fichier == False:
            self.warninglabel.setText("WARNING: Veuillez ouvrir une base de données au prealable avec le boutton OUVRIR")    

        #remplissage de listewidget
        for num_ligne, value_ligne in enumerate(df):
            column = 0
            for value in value_ligne:
                value = str(value)
                item = QTableWidgetItem(value)
                self.tableWidget.setItem(num_ligne, column, item)
                column += 1
        

    def add_table(self):
        Fenetre3(self, self.fichier)

    def rem_table(self):
        tableName = self.box.currentText()

        # application des modifs dans le fichier sqlite
        con = sqlite3.connect(self.fichier)
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS {0};".format(tableName))

        #realoading du fichier sqlite
        self.charger()
        self.ajout_combobox(self.tables_list)

    def funct_nouveau(self, bibliothequeNom):
        pwd = os.getcwd()
        pwd = pwd.replace("\\","/")
        self.fichier = pwd + "/Data/" + bibliothequeNom + ".sqlite"
        print("le nouveau fichier sqlite est : ", self.fichier)
        
        self.tableWidget.clear()
        self.vidange_Layout()
        self.ajout_combobox(self.parent0.rt)
        self.tableWidget.setColumnCount(len(self.parent0.rc))
        self.tableWidget.setRowCount(1)
        self.tableWidget.setHorizontalHeaderLabels(retrieved_champs)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tableWidget)
        self.sauvegarder.setEnabled(True)

    def ouvrir_db(self):#ouvrir une DB
        self.setEnabled(False) 
        self.fichier = QFileDialog.getOpenFileName(filter = "sqlite (*.sqlite)")[0]
        self.setEnabled(True)
        if self.fichier:
            self.charger()
            self.ajout_combobox(self.tables_list)
        else:
            return

    def ajouter_ligne(self):#ajouter une ligne
        #ajouter un nouveau row
        self.position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(self.position)

    def delete(self):#supprimer une ligne
        self.position = self.tableWidget.currentRow()
        self.tableWidget.removeRow(self.position)
    
    def ecrire(self):
        try:
            #print(self.fichier)
            dataframe =[]#remplissage d'une dataframe 
            fin_de_ligne = self.tableWidget.rowCount()
            
            #recupétartion des infos Tables et colonnes
            table = self.box.currentText()
            colonnes = []

            for i in range(self.tableWidget.columnCount()):
                colonnes.append(self.tableWidget.horizontalHeaderItem(i).text())
            
            for l in range(fin_de_ligne):
                liste = []
                for c in range(len(colonnes)):
                    item = self.tableWidget.item(l,c)             
                    liste.append(item.text())
                dataframe.append(tuple(liste))
            print("la table est ", table)
            print("dataframe", dataframe)

            #ecriture sur le curseur
            str = "("
            for c in range(len(dataframe[0])):
                str = str + "?,"
            str = list(str)
            del str[-1]
            str = "".join(str)
            str = str + ")"
            #correctif du bug 1, supprimer la table ou tous les elements de la table
            try:
                self.cursor.execute("DELETE FROM {}".format(table))
                self.connection.commit()
            except:
                pass

            for tu in dataframe:
                try :
                    self.cursor.execute("REPLACE INTO {0} VALUES {1}".format(table, str),tu)
                    print("ecriture de ", tu)
                except :
                    self.connection = sqlite3.connect(self.fichier)
                    self.cursor = self.connection.cursor()
                    s = "("
                    rc = colonnes
                    for i in rc :
                        i += ", "
                        s += i
                    s = list(s)
                    s.pop(-1)
                    s.pop(-1)
                    s = "".join(s)
                    s += ")"
                    print("les colonnes", s)
                    self.cursor.execute("CREATE TABLE {0}{1}".format(table, s))
                    print("les tuples",tu)
                    print("ecriture de nouveau")
                    self.cursor.execute("REPLACE INTO {0} VALUES {1}".format(table, str),tu)
            self.connection.commit()
        except:
            print("sauvegarde d'une table vide impossible")
    #vidange de self.gridLayout
    def vidange_Layout(self):
        try :
            for j in range(self.gridLayout.count()):
                i = self.gridLayout.itemAt(j)
                self.gridLayout.removeItem(i)
        except:
            pass

    def charger(self):#charger la Db
        vidange_Layout(self)
        self.initTableWidget()
        self.gridLayout.addWidget(self.tableWidget)
        #recuperation des données dans un tuple
        print(self.fichier)
        try :
            self.connection = sqlite3.connect(self.fichier)
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            self.tables = self.cursor.fetchall()

            self.tables_list = []
            for t in self.tables:
                self.tables_list.append(t[0])
            
            try:
                self.tables_list.remove("sqlite_sequence")
            except:
                pass
            
            #ajout du choix de table
            self.choosenTable = self.box.currentText()
            if self.choosenTable == None or self.choosenTable == "":
                self.choosenTable = self.tables_list[0]
            
            print('le choosentable est :', self.choosenTable)
            self.warninglabel.setText("WARNING: Base chargée")
            print(self.fichier)
            
            df = []
            listrow = 0
            for row in self.cursor.execute("SELECT * FROM "+str(self.choosenTable)):
                listrow += 1
                df.append(list(row))
            

            self.tableWidget.setRowCount(len(df))

            #capture des champs de la table
            self.champs = []
            for i, j in enumerate(list(self.cursor.description)):
                self.champs.append(self.cursor.description[i][0])
            
            #ajout des champs dans les headers
            self.tableWidget.setColumnCount(len(self.champs))
            self.tableWidget.setHorizontalHeaderLabels(self.champs)
            self.tableWidget.horizontalHeader().setStretchLastSection(True)
            #self.tableWidget.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
            
        except:
            pass
        
        if self.fichier == False:
            self.warninglabel.setText("WARNING: Veuillez ouvrir une base de données au prealable avec le boutton OUVRIR")    

        #remplissage de listewidget
        for num_ligne, value_ligne in enumerate(df):
            column = 0
            for value in value_ligne:
                value = str(value)
                item = QTableWidgetItem(value)
                self.tableWidget.setItem(num_ligne, column, item)
                column += 1
        
        self.sauvegarder.setEnabled(True)

        #forcer le changement de (je m'en souviens plus de ce que j'allais faire ici)  
        #self.constinit = True 

    def ajout_combobox(self,table):#remplir la combobox
        self.box.clear()
        self.boxnumber = 0
        try :
            self.box.addItems(table)
        except :
            pass

    def recherche(self,signal):
        self.tableWidget.setCurrentItem(None)

        if not signal:
            return

        found_items = self.tableWidget.findItems(signal, QtCore.Qt.MatchContains)
        if found_items :
            for item in found_items:
                item.setSelected(True)
        
    def filtrage(self,signal):
        if self.filterBox == 0:
            return

        found_items = self.tableWidget.findItems(signal, QtCore.Qt.MatchContains)

        self.tableWidget.setCurrentItem(None)
        found_rows = []

        if signal == None or signal == "":
            self.charger()
            return

        if found_items :
            for item in found_items:
                self.tableWidget.setCurrentItem(item)
                found_rows.append(self.tableWidget.currentRow())
            
            found_rows = set(found_rows)
            print("les lignes trouvées sont :", found_rows)

            #recuperation des dataframmes temporaires
            df_temp_1 = []
            for l in found_rows:
                df_temp_2 = []
                for c in range(len(self.champs)):
                    df_temp_2.append(self.tableWidget.item(l, c).text())
                df_temp_1.append(df_temp_2)
            print(df_temp_1)

            #creation d'une table temporaire de recherche
            self.tableTemp = QTableWidget()
            print(self.tableTemp.parent())
            self.tableTemp.setRowCount(len(df_temp_1))
            self.tableTemp.setColumnCount(len(df_temp_2))
            self.tableTemp.setHorizontalHeaderLabels(self.champs)
            self.tableTemp.horizontalHeader().setStretchLastSection(True)
            
            for num_ligne, value_ligne in enumerate(df_temp_1):
                column = 0
                for value in value_ligne:
                    value = str(value)
                    i = QTableWidgetItem(value)
                    self.tableTemp.setItem(num_ligne, column, i)
                    column += 1

            vidange_Layout(self)
            self.gridLayout.addWidget(self.tableTemp)

class Fenetre2(QDialog):
    def __init__(self, parent1):
        super(Fenetre2, self).__init__()
        loadUi("UI/Fenetre2.ui",self)
        parent1.setEnabled(False)

        self.parent1 = parent1

        self.rt = parent1.parent0.rt
        self.rc = parent1.parent0.rc

        if self.rc != "" or self.rc != None:
           self.rc.clear()
        if self.rt != "" or self.rt != None:
            self.rt.clear()

        #UI
        self.widget = QtWidgets.QStackedWidget()
        self.widget.addWidget(self)
        self.widget.show()

        #Bouttons
        self.annuler.clicked.connect(self.quitter)
        self.OK.setEnabled(False)
        self.tableLine.textChanged.connect(self.unlock0)
        self.champsEdit.textChanged.connect(self.unlock1)
        self.bibliothequeEdit.textChanged.connect(self.unlock2)
        self.OK.clicked.connect(self.ok)
        self.df = []

    def unlock2(self, signal):
        if signal == None or signal == "" or self.tableLine.text() == "":
            self.OK.setEnabled(False)
        else:
            self.biblioLineText = "exist"
            
    def unlock1(self, signal):
        if signal or self.champsEdit.text() != "" and self.tablelineText == "exist" and self.biblioLineText == "exist": #si le texte est vide alors on le desactive
            try :
                splitter = ","
                noises = ["", " "]
                x = self.champsEdit.text().split(splitter)
                print("x before cleaning :", x)
                try:
                    x.remove("")
                    print("x after removing :", x)
                except:
                    pass
                print(len(x))

                #####data cleaning
                col = []
                for item in x:
                    col.append(item.rstrip(" "))
                
                if len(col) > 1 : 
                    self.OK.setEnabled(True)
                else: self.OK.setEnabled(False)
            except:
                pass
        else: self.OK.setEnabled(False)
        
    def unlock0(self, signal):
        if signal == None or signal == "" or self.tableLine.text() == "":
            self.OK.setEnabled(False)
        else:
            self.tableLineText = "exist"

    def createFileandTable(self, nomFichier, table, colonnes):
        print(table, colonnes)

        conn = sqlite3.connect(nomFichier)
        cur = conn.cursor()
        colonnes_str = ', '.join(colonnes)
        query = "CREATE TABLE IF NOT EXISTS {0}({1});".format(table[0], colonnes_str)
        print(query)
        
        cur.execute(query)
        conn.commit()

    def quitter(self):
        self.parent1.setEnabled(True) 
        #if self.rc !="" and self.rt !="" :
            #execution de funct_nouveau de la classe fenetre1
        #    fenetre0.fenetre1.funct_nouveau()
        self.widget.close()
        self.close()

    def ok(self):
        #recuperation des colonnes
        str = self.champsEdit.text()
        str = str + ","
        nom = ""
        noms = []
        for c in str :
            nom = nom + c
            if c == ",":
                nom = list(nom)
                nom.remove(',')
                nom = "".join(nom)
                noms.append(nom)
                nom = ""
        for c in noms:
            self.rc.append(c.rstrip(" "))
        print(self.rc)
        
        #recuperation des tables
        str1 = self.tableLine.text()
        str1 = str1 + ","
        nom1 = ""
        noms1 = []
        for c in str1 :
            nom1 = nom1 + c
            if c == ",":
                nom1 = list(nom1)
                nom1.remove(',')
                nom1 = "".join(nom1)
                noms1.append(nom1)
                nom1 = ""

        for c in noms1:
            self.rt.append(c)
        print(self.rt)
        
        #recupération du nom de fichier
        self.db = self.bibliothequeEdit.text()
        pwd = os.getcwd()
        pwd = pwd.replace("\\","/")
        fichier = pwd + "/Data/" + self.db + ".sqlite"
        print("le nouveau fichier sqlite est : ", fichier)


        self.parent1.setEnabled(True) 
        if self.rc !="" and self.rt !="" and self.db !="":
            #execution de funct_nouveau de la classe fenetre1
            fenetre0.fenetre1.funct_nouveau(self.db)
            self.createFileandTable(fichier, self.rt, self.rc)
        self.widget.close()
        self.close()


class Fenetre3(QDialog):
    def __init__(self, parent1, fichier):
        super(Fenetre3, self).__init__()
        loadUi("UI/Fenetre3.ui",self)
        parent1.setEnabled(False)

        self.nomFichier = fichier
        self.parent1 = parent1

        self.rt = parent1.parent0.rt
        self.rc = parent1.parent0.rc

        #if self.rc != "" or self.rc != None:
        #   self.rc.clear()
        #if self.rt != "" or self.rt != None:
        #    self.rt.clear()

        #UI
        self.widget = QtWidgets.QStackedWidget()
        self.widget.addWidget(self)
        self.widget.show()

        #Bouttons
        self.annuler.clicked.connect(self.quitter)
        self.OK.setEnabled(False)
        self.tableLine.textChanged.connect(self.unlock0)
        self.champsEdit.textChanged.connect(self.unlock1)
        self.OK.clicked.connect(self.ok)
        self.df = []

    def unlock1(self, signal):
        if signal or self.champsEdit.text() != "" and self.tablelineText == "exist": #si le texte est vide alors on le desactive
            try :
                splitter = ","
                x = self.champsEdit.text().split(splitter)
                print("x before cleaning :", x)
                try:
                    x.remove("")
                    print("x after removing :", x)
                except:
                    pass
                print(len(x))
                if len(x) > 1 :
                    self.OK.setEnabled(True)
                else: self.OK.setEnabled(False)
            except:
                pass
        else: self.OK.setEnabled(False)
        
    def unlock0(self, signal):
        if signal == None or signal == "" or self.tableLine.text() == "":
            self.OK.setEnabled(False)
        else:
            self.tableLineText = "exist"
            
    def insertTable(self):
        conn = sqlite3.connect(self.nomFichier)
        colonnes_str = ', '.join(self.rc)
        conn.execute(f"CREATE TABLE IF NOT EXISTS {self.rt[0]} ({colonnes_str})")
        fenetre0.fenetre1.tables_list.append(self.rt[0])
        fenetre0.fenetre1.charger()
        fenetre0.fenetre1.ajout_combobox(fenetre0.fenetre1.tables_list)
            
    def quitter(self):
        self.parent1.setEnabled(True)
        self.widget.close()
        self.close()

    def ok(self):
        #recuperation des colonnes
        str = self.champsEdit.text()
        str = str + ","
        nom = ""
        noms = []
        for c in str :
            nom = nom + c
            if c == ",":
                nom = list(nom)
                nom.remove(',')
                nom = "".join(nom)
                noms.append(nom)
                nom = ""
        for c in noms:
            self.rc.append(c)
        print(self.rc)
        
        #recuperation des tables
        str1 = self.tableLine.text()
        str1 = str1 + ","
        nom1 = ""
        noms1 = []
        for c in str1 :
            nom1 = nom1 + c
            if c == ",":
                nom1 = list(nom1)
                nom1.remove(',')
                nom1 = "".join(nom1)
                noms1.append(nom1)
                nom1 = ""

        for c in noms1:
            self.rt.append(c)
        print(self.rt)
        
        self.insertTable()
        self.quitter()

#vidange de self.gridLayout
def vidange_Layout(self):
    for j in range(self.gridLayout.count()):
        i = self.gridLayout.itemAt(j)
        self.gridLayout.removeItem(i)

"""Main"""
cond_annuler = False
retrieved_champs = []
retrieved_table = []
app = QApplication(sys.argv)

if cond_annuler == False:
    swidget = QtWidgets.QStackedWidget()
    fenetre0 = Fenetre0(retrieved_champs, retrieved_table)
    fenetre0.loading()
    #swidget.close()
    #fenetre0.func_ouvrir()
    #swidget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")


"""sql commands
cur.execute("CREATE TABLE membres (age INTEGER, nom TEXT, taille REAL)")
cur.execute("INSERT INTO membres(age,nom,taille) VALUES(15,'Blumâr',1.57)")
conn.commit()
cur.close()
conn.close()

CREATE TABLE IF NOT EXISTS positions ( id integer PRIMARY KEY, title text NOT NULL, min_salary numeric )
CREATE UNIQUE INDEX idx_positions_title ON positions (title);
cur.execute("REPLACE INTO positions (title, min_salary) VALUES (?,?,?)",tuple)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
"""