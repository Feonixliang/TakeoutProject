import mysql.connector
from mysql.connector import Error


def create_database_tables():
    try:
        # 连接MySQL数据库（需提前创建数据库）
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456',
            database='takeout'
        )
        cursor = conn.cursor()

        # 创建账户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Account (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            AccountType ENUM('Rider', 'Customer', 'Merchant','pending') DEFAULT 'pending'
        ) ENGINE=InnoDB;
        ''')

        # 创建骑手表
        cursor.execute('''
        CREATE TABLE Rider (
          RId int NOT NULL,
          RName varchar(20) NOT NULL,
          RPhone varchar(20) NOT NULL,
          PRIMARY KEY (RId),
          UNIQUE KEY RName (RName),
          UNIQUE KEY RPhone (RPhone),
          CONSTRAINT const_Rider_Acc FOREIGN KEY (RId) REFERENCES Account (user_id)
            ) ENGINE=InnoDB;
        ''')

        # 创建客户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Customer (
            CId int NOT NULL,
            CName varchar(50) NOT NULL,
            CPhone varchar(30) NOT NULL,
            CAddress varchar(200) NOT NULL,
            CBalance decimal(10,2) NOT NULL,
            PRIMARY KEY (CId),
            UNIQUE KEY CName (CName),
            UNIQUE KEY CPhone (CPhone),
            CONSTRAINT const_Customer_Acc FOREIGN KEY (CId) REFERENCES Account (user_id)
        ) ENGINE=InnoDB;
        ''')

        # 创建商家表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Merchant (
            MId int NOT NULL,
            MName varchar(100) NOT NULL,
            MPhone varchar(30) NOT NULL,
            MAddress varchar(200) NOT NULL,
            MBalance decimal(10,2) NOT NULL,
            PRIMARY KEY (MId),
            UNIQUE KEY MPhone (MPhone),
            CONSTRAINT const_Merchantr_Acc FOREIGN KEY (MId) REFERENCES Account (user_id)
        ) ENGINE=InnoDB;
        ''')



        # 创建菜品表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Dishes (
            DId INT PRIMARY KEY AUTO_INCREMENT,
            DName VARCHAR(100) NOT NULL,
            DPrice DECIMAL(10,2) NOT NULL,
            DCategory VARCHAR(50)
        ) ENGINE=InnoDB;
        ''')

        # 创建菜品商家关系表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS MerchantDishes (
            DId INT NOT NULL,
            MId INT NOT NULL,
            PRIMARY KEY (DId, MId),  -- 定义联合主键
            FOREIGN KEY (DId) REFERENCES Dishes(DId),  -- 外键约束（假设菜品表主键为 DishId）
            FOREIGN KEY (MId) REFERENCES Merchant(MId)  -- 外键约束（假设商家表主键为 MerchantId）
        ) ENGINE=InnoDB;
        ''')

        # 创建订单表（处理保留字）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS `Order` (
            OId INT PRIMARY KEY AUTO_INCREMENT,
            CId INT NOT NULL,
            MId INT NOT NULL,
            RId INT,
            TotalPrice DECIMAL(10,2) NOT NULL,
            status varchar(10,2) ,
            FOREIGN KEY (CId) REFERENCES Customer(CId),
            FOREIGN KEY (MId) REFERENCES Merchant(MId),
            FOREIGN KEY (RId) REFERENCES Rider(RId)
        ) ENGINE=InnoDB;
        ''')

        # 创建订单-菜品关联表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS OrderDishes (
            OId INT,
            DId INT,
            Quantity INT NOT NULL DEFAULT 1,
            FOREIGN KEY (OId) REFERENCES `Order`(OId),
            FOREIGN KEY (DId) REFERENCES Dishes(DId)
        ) ENGINE=InnoDB;
        ''')

        print("所有表已成功创建！")

    except Error as e:
        print(f"数据库错误: {e}")
        conn.rollback()  # 发生错误时回滚
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# 执行函数
create_database_tables()