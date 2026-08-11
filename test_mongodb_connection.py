import sys
import certifi
import pymongo
from usvisa.constants import MONGODB_URL_KEY

ca = certifi.where()

def test_mongo():
    print("========== Probando Conexión a MongoDB Atlas ==========")
    print(f"URL: {MONGODB_URL_KEY[:35]}...")
    
    # Intento 1: Standard con certifi y tlsAllowInvalidCertificates
    try:
        print("\nPrueba 1: Conectando con tlsCAFile=certifi.where() y tlsAllowInvalidCertificates=True...")
        client = pymongo.MongoClient(MONGODB_URL_KEY, tlsCAFile=ca, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
        db = client['usvisa']
        coll = db['visa_data']
        count = coll.count_documents({})
        print(f"✔ ¡ÉXITO! Documentos encontrados en la colección 'visa_data': {count}")
        return
    except Exception as e:
        print(f"❌ Falló Prueba 1: {e}")

    # Intento 2: Sin certifi, permitiendo certificados no válidos
    try:
        print("\nPrueba 2: Conectando con tls=True, tlsAllowInvalidCertificates=True...")
        client = pymongo.MongoClient(MONGODB_URL_KEY, tls=True, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
        db = client['usvisa']
        coll = db['visa_data']
        count = coll.count_documents({})
        print(f"✔ ¡ÉXITO! Documentos encontrados en la colección 'visa_data': {count}")
        return
    except Exception as e:
        print(f"❌ Falló Prueba 2: {e}")

    print("\n⚠️ SI AMBAS PRUEBAS FALLAN CON 'TLSV1_ALERT_INTERNAL_ERROR':")
    print("Significa que la dirección IP de tu red actual NO está agregada a la lista de acceso (Network Access / IP Access List) en la consola de MongoDB Atlas.")

if __name__ == "__main__":
    test_mongo()
