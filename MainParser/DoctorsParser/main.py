from doctors_list import get_doctors, process_doctor
from DB import store_services

if __name__ == "__main__":
    base_url = "https://clinica.chitgma.ru/diagnosticheskaya-poliklinika"
    doctors = get_doctors(base_url)
    all_results = [process_doctor(doctor) for doctor in doctors]

    # Вывод результатов
    for res in all_results:
        doctor = res['doctor']
        print(f"\nВрач: {doctor['name']}")
        if res['services']:
            for service in res['services']:
                print(f"  - {service['service']} : {service['price']} руб.")
        else:
            print("  Нет данных по услугам в этом разделе.")

    # Запись данных в Postgres
    store_services(all_results)