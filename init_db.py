from database import engine, Base, SessionLocal
from models import Agent, Client
from werkzeug.security import generate_password_hash
from datetime import datetime
import random

def generate_moroccan_phone():
    """Generate a random Moroccan phone number"""
    prefixes = ['06', '07']
    return f'+212{random.choice(prefixes)}{random.randint(10000000, 99999999)}'

def generate_moroccan_name():
    """Generate a random Moroccan name"""
    first_names = [
        'Mohammed', 'Ahmed', 'Youssef', 'Ali', 'Omar', 'Hamza', 'Karim',
        'Fatima', 'Aisha', 'Maryam', 'Nour', 'Layla', 'Sara', 'Zineb'
    ]
    last_names = [
        'Alami', 'Bennani', 'Cherkaoui', 'Idrissi', 'Fassi', 'Tazi',
        'Saidi', 'Benjelloun', 'Mansouri', 'Rachidi', 'El Amrani'
    ]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def init_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(Client).delete()
        db.query(Agent).delete()
        
        # Create agents
        agents = [
            {
                'username': 'credit_agent',
                'password': generate_password_hash('password1'),
                'full_name': 'Mohammed Alami',
                'window_name': 'Guichet Crédit'
            },
            {
                'username': 'account_agent',
                'password': generate_password_hash('password2'),
                'full_name': 'Fatima Bennani',
                'window_name': 'Guichet Compte'
            },
            {
                'username': 'loan_agent',
                'password': generate_password_hash('password3'),
                'full_name': 'Karim Benani',
                'window_name': 'Guichet Prêt'
            }
        ]
        
        for agent_data in agents:
            agent = Agent(**agent_data)
            db.add(agent)
            
        db.commit()
        print("Agents created successfully!")

        # Service types and windows
        services = {
            'Credit Service': 'Guichet Crédit',
            'Account Opening': 'Guichet Compte',
            'Loan Application': 'Guichet Prêt',
            'General Inquiry': 'Guichet Compte'
        }

        # Generate mock clients
        position_counter = {window: 1 for window in set(services.values())}
        
        num_clients = 25
        for i in range(num_clients):
            service_type = random.choice(list(services.keys()))
            window = services[service_type]
            position = position_counter[window]
            position_counter[window] += 1
            
            # Random wait time based on position
            wait_time = position * random.randint(5, 15)
            
            # Create client
            client = Client(
                name=generate_moroccan_name(),
                phone_number=generate_moroccan_phone(),
                service_type=service_type,
                status='waiting',
                position=position,
                wait_time=wait_time,
                check_in_time=datetime.now(),
                assigned_window=window
            )
            db.add(client)
        
        db.commit()
        print(f"Created {num_clients} mock clients successfully!")
        
        # Print summary
        for window in set(services.values()):
            count = db.query(Client).filter(
                Client.assigned_window == window,
                Client.status == 'waiting'
            ).count()
            print(f"{window}: {count} clients waiting")
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        db.rollback()
    finally:
        db.close()

def add_to_queue(phone_number, service_type):
    print("\n=== Adding Client to Queue ===")
    print(f"Phone: {phone_number}")
    print(f"Service: {service_type}")
    
    try:
        # Verify database connection
        db = SessionLocal()
        print("Database connection established")
        
        # Verify service type exists
        if service_type not in SERVICE_DESCRIPTIONS:
            print(f"Invalid service type: {service_type}")
            return None, None, None
            
        try:
            # Get the appropriate window name
            window_name = SERVICE_WINDOW_MAP.get(service_type)
            
            # Create new client with minimum required fields
            new_client = Client(
                phone_number=phone_number,
                name="Client via Chat",  # Default name
                service_type=service_type,
                status="waiting",
                position=1,  # We'll update this later
                wait_time=15,  # Default wait time
                assigned_window=window_name
            )
            
            print(f"Created client object: {new_client.__dict__}")
            
            # Try adding to database
            db.add(new_client)
            db.commit()
            db.refresh(new_client)
            
            print(f"Successfully added client with ID: {new_client.id}")
            return new_client.id, 1, 15
            
        except Exception as e:
            print(f"Error creating client: {str(e)}")
            import traceback
            print(traceback.format_exc())
            db.rollback()
            return None, None, None
            
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None, None, None
    finally:
        try:
            db.close()
            print("Database connection closed")
        except:
            pass
        print("=== End of Add to Queue ===\n")

if __name__ == "__main__":
    init_database() 