<template>
  <div class="employee-cabinet">
    <h1>Кабинет сотрудника</h1>
    
    <div class="tabs">
      <button :class="{ active: activeTab === 'clients' }" @click="setActiveTab('clients')">Клиенты</button>
      <button :class="{ active: activeTab === 'contracts' }" @click="setActiveTab('contracts')">Договоры</button>
      <button :class="{ active: activeTab === 'fines' }" @click="setActiveTab('fines')">Типы штрафов</button>
      <button :class="{ active: activeTab === 'cars' }" @click="setActiveTab('cars')">Автомобили</button>
      <button :class="{ active: activeTab === 'services' }" @click="setActiveTab('services')">Услуги</button>
      <button :class="{ active: activeTab === 'employees' }" @click="setActiveTab('employees')">Сотрудники</button>
      <button :class="{ active: activeTab === 'reports' }" @click="setActiveTab('reports')">Отчеты</button>
    </div>
    
    <!-- Клиенты -->
    <div v-if="activeTab === 'clients'" class="tab-content">
      <h2>Список клиентов</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>ФИО</th>
            <th>Email</th>
            <th>Пол</th>
            <th>Телефоны</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="client in clients" :key="client.ID_клиента">
            <td>{{ client.ID_клиента }}</td>
            <td>{{ client.ФИО }}</td>
            <td>{{ client.email }}</td>
            <td>{{ client.Пол }}</td>
            <td>
              <span v-for="(phone, index) in client.Телефоны" :key="index">
                {{ phone.Номер }} ({{ phone.Тип }})
                <br v-if="index < client.Телефоны.length - 1">
              </span>
            </td>
            <td>
              <button @click="viewClientDocuments(client.ID_клиента)" class="btn-view">Документы</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Договоры -->
    <div v-if="activeTab === 'contracts'" class="tab-content">
      <h2>Список договоров</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Клиент</th>
            <th>Автомобиль</th>
            <th>Дата начала</th>
            <th>Дата окончания</th>
            <th>Статус</th>
            <th>Стоимость</th>
            <th>Статус оплаты</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="contract in contracts" :key="contract.ID_договора">
            <td>{{ contract.ID_договора }}</td>
            <td>{{ contract.Клиент }}</td>
            <td>{{ contract.Автомобиль }}</td>
            <td>{{ formatDate(contract.Дата_начала) }}</td>
            <td>{{ formatDate(contract.Дата_окончания) }}</td>
            <td>{{ contract.Статус_договора }}</td>
            <td>{{ contract.Стоимость }} ₽</td>
            <td>
              <select 
                v-model="contract.Статус_оплаты" 
                @change="updatePaymentStatus(contract.ID_договора, contract.Статус_оплаты)"
                class="status-select"
              >
                <option value="Оплачено">Оплачено</option>
                <option value="В ожидании">В ожидании</option>
                <option value="Отклонено">Отклонено</option>
              </select>
            </td>
            <td>
              <button @click="openAddFineModal(contract)" class="add-button">Добавить штраф</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Штрафы -->
    <div v-if="activeTab === 'fines'" class="tab-content">
      <h2>Типы штрафов</h2>
      
      <div class="actions-bar">
        <button @click="showAddFineTypeModal = true" class="add-button">Добавить новый тип штрафа</button>
      </div>
      
      <!-- Типы штрафов -->
      <div class="fines-types-section">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Стоимость</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="fine in fines" :key="fine.ID_штрафа">
              <td>{{ fine.ID_штрафа }}</td>
              <td>{{ fine.Название }}</td>
              <td>
                <div class="price-edit-container">
                  <input 
                    type="number" 
                    v-model="fine.Стоимость"
                    @blur="updateFinePrice(fine.ID_штрафа, fine.Стоимость)"
                    class="edit-input price-input"
                  >
                  <span class="currency">₽</span>
                </div>
              </td>
              <td>
                <button @click="deleteFine(fine.ID_штрафа)" class="delete-button">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Автомобили -->
    <div v-if="activeTab === 'cars'" class="tab-content">
      <h2>Автомобили</h2>
      <button @click="showAddCarModal = true" class="add-button">Добавить автомобиль</button>
      
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Марка</th>
            <th>Модель</th>
            <th>Год выпуска</th>
            <th>Категория</th>
            <th>Стоимость (в день)</th>
            <th>Статус</th>
            <th>Дата техосмотра</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="car in cars" :key="car.ID_автомобиля">
            <td>{{ car.ID_автомобиля }}</td>
            <td>{{ car.Марка }}</td>
            <td>{{ car.Модель }}</td>
            <td>{{ car.Год_выпуска }}</td>
            <td>{{ car.Категория }}</td>
            <td>
              <div class="price-edit-container">
                <input 
                  type="number" 
                  v-model="car.Стоимость"
                  @blur="updateCarPrice(car.ID_автомобиля, car.Стоимость)"
                  class="edit-input price-input"
                >
                <span class="currency">₽</span>
              </div>
            </td>
            <td>
              <select 
                v-model="car.Статус_авто" 
                @change="updateCarStatus(car.ID_автомобиля, car.Статус_авто)"
                class="status-select"
              >
                <option value="Доступен">Доступен</option>
                <option value="В аренде">В аренде</option>
                <option value="На обслуживании">На обслуживании</option>
              </select>
            </td>
            <td>
              <input 
                type="date" 
                v-model="car.Дата_техосмотра"
                @blur="updateCarInspectionDate(car.ID_автомобиля, car.Дата_техосмотра)"
                class="edit-input date-input"
              >
            </td>
            <td>
              <button @click="deleteCar(car.ID_автомобиля)" class="delete-button">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Услуги -->
    <div v-if="activeTab === 'services'" class="tab-content">
      <h2>Услуги</h2>
      
      <div class="actions-bar">
        <button @click="showAddServiceModal = true" class="add-button">Добавить новую услугу</button>
      </div>
      
      <div class="services-section">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Стоимость</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="service in services" :key="service.ID_услуги">
              <td>{{ service.ID_услуги }}</td>
              <td>{{ service.Название }}</td>
              <td>
                <div class="price-edit-container">
                  <input 
                    type="number" 
                    v-model="service.Стоимость"
                    @blur="updateServicePrice(service.ID_услуги, service.Стоимость)"
                    class="edit-input price-input"
                  >
                  <span class="currency">₽</span>
                </div>
              </td>
              <td>
                <button @click="deleteService(service.ID_услуги)" class="delete-button">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Сотрудники -->
    <div v-if="activeTab === 'employees'" class="tab-content">
      <h2>Сотрудники</h2>
      
      <div class="actions-bar">
        <button @click="showAddEmployeeModal = true" class="add-button">Добавить нового сотрудника</button>
      </div>
      
      <div class="employees-section">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>ФИО</th>
              <th>Должность</th>
              <th>Телефон</th>
              <th>Email</th>
              <th>Оклад</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="employee in employees" :key="employee.ID_сотрудника">
              <td>{{ employee.ID_сотрудника }}</td>
              <td>{{ employee.ФИО_с }}</td>
              <td>{{ employee.Должность }}</td>
              <td>{{ employee.Телефон_с }}</td>
              <td>{{ employee.email }}</td>
              <td>
                <div class="price-edit-container">
                  <input 
                    type="number" 
                    v-model="employee.Оклад"
                    @blur="updateEmployeeSalary(employee.ID_сотрудника, employee.Оклад)"
                    class="edit-input price-input"
                  >
                  <span class="currency">₽</span>
                </div>
              </td>
              <td>
                <button @click="deleteEmployee(employee.ID_сотрудника)" class="delete-button">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Отчеты -->
    <div v-if="activeTab === 'reports'" class="tab-content">
      <h2>Отчеты</h2>
      
      <div class="report-selection">
        <div class="report-header">
          <h3>Выберите тип отчета:</h3>
          <div class="report-types">
            <select v-model="selectedReport">
              <!-- Отчеты по клиентам -->
              <optgroup label="Отчеты по клиентам">
                <option value="clients">Все клиенты</option>
                <option value="overdue_clients">Клиенты с просрочками</option>
              </optgroup>
              
              <!-- Отчеты по автомобилям -->
              <optgroup label="Отчеты по автомобилям">
                <option value="cars">Все автомобили</option>
                <option value="cars_in_maintenance">Автомобили на обслуживании</option>
                <option value="popular_cars">Популярные модели</option>
                <option value="insurances">Страховки</option>
              </optgroup>
              
              <!-- Отчеты по договорам -->
              <optgroup label="Отчеты по договорам">
                <option value="active_contracts">Активные договоры</option>
                <option value="completed_contracts">Завершенные договоры</option>
                <option value="overdue_payments">Просроченные платежи</option>
                <option value="revenue">Доходы по договорам</option>
              </optgroup>
              
              <!-- Отчеты по штрафам и услугам -->
              <optgroup label="Прочие отчеты">
                <option value="fines">Штрафы</option>
                <option value="popular_services">Популярные услуги</option>
              </optgroup>
            </select>
          </div>
        </div>
        
        <!-- Фильтры для отчета по штрафам -->
        <div v-if="selectedReport === 'fines'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item">
              <label>Дата начала:</label>
              <input type="date" v-model="fineReportFilters.startDate">
            </div>
            <div class="filter-item">
              <label>Дата окончания:</label>
              <input type="date" v-model="fineReportFilters.endDate">
            </div>
            <div class="filter-item">
              <label>Клиент:</label>
              <select v-model="fineReportFilters.clientId">
                <option value="">Все клиенты</option>
                <option v-for="client in clients" :key="client.ID_клиента" :value="client.ID_клиента">{{ client.ФИО }}</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- Фильтры для отчета по автомобилям -->
        <div v-if="selectedReport === 'cars'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item">
              <label>Статус:</label>
              <select v-model="carReportFilters.status">
                <option value="">Все статусы</option>
                <option value="Доступен">Доступен</option>
                <option value="В аренде">В аренде</option>
                <option value="На обслуживании">На обслуживании</option>
              </select>
            </div>
            <div class="filter-item">
              <label>Категория:</label>
              <select v-model="carReportFilters.category">
                <option value="">Все категории</option>
                <option value="Эконом">Эконом</option>
                <option value="Бизнес">Бизнес</option>
                <option value="Премиум">Премиум</option>
              </select>
            </div>
            <div class="filter-item">
              <label>Год выпуска (от):</label>
              <input type="number" v-model="carReportFilters.yearFrom" min="1990" max="2030">
            </div>
            <div class="filter-item">
              <label>Год выпуска (до):</label>
              <input type="number" v-model="carReportFilters.yearTo" min="1990" max="2030">
            </div>
          </div>
        </div>
        
        <!-- Фильтры для отчета по клиентам -->
        <div v-if="selectedReport === 'clients'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item">
              <label>Пол:</label>
              <select v-model="clientReportFilters.gender">
                <option value="">Все</option>
                <option value="м">Мужской</option>
                <option value="ж">Женский</option>
              </select>
            </div>
            <div class="filter-item">
              <label>Количество бронирований (от):</label>
              <input type="number" v-model="clientReportFilters.bookingsFrom" min="0">
            </div>
          </div>
        </div>
        
        <!-- Фильтры для отчета по бронированиям -->
        <div v-if="selectedReport === 'bookings'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item">
              <label>Дата начала:</label>
              <input type="date" v-model="bookingReportFilters.startDate">
            </div>
            <div class="filter-item">
              <label>Дата окончания:</label>
              <input type="date" v-model="bookingReportFilters.endDate">
            </div>
            <div class="filter-item">
              <label>Способ оплаты:</label>
              <select v-model="bookingReportFilters.paymentMethod">
                <option value="">Все</option>
                <option value="Карта">Карта</option>
                <option value="Наличные">Наличные</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- Фильтры для отчета по прибыли -->
        <div v-if="selectedReport === 'profit'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item">
              <label>Период:</label>
              <select v-model="profitReportFilters.period">
                <option value="day">День</option>
                <option value="week">Неделя</option>
                <option value="month">Месяц</option>
                <option value="quarter">Квартал</option>
                <option value="year">Год</option>
              </select>
            </div>
            <div class="filter-item">
              <label>Дата начала:</label>
              <input type="date" v-model="profitReportFilters.startDate">
            </div>
            <div class="filter-item">
              <label>Дата окончания:</label>
              <input type="date" v-model="profitReportFilters.endDate">
            </div>
          </div>
        </div>
        
        <!-- Фильтры для отчета по клиентам с просрочками -->
        <div v-if="selectedReport === 'overdue_clients'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item">
              <label>Количество просрочек (от):</label>
              <input type="number" v-model="overdueClientsFilters.overdueCount" min="1">
            </div>
            <div class="filter-item">
              <label>Тип просрочки:</label>
              <select v-model="overdueClientsFilters.type">
                <option value="all">Все</option>
                <option value="payments">Только платежи</option>
                <option value="fines">Только штрафы</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- Фильтры для отчета по автомобилям на обслуживании -->
        <div v-if="selectedReport === 'cars_in_maintenance'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item checkbox-container">
              <label>Включить автомобили:</label>
              <div class="checkbox-group">
                <label>
                  <input type="checkbox" v-model="carsInMaintenanceFilters.includeMaintenance">
                  На обслуживании
                </label>
                <label>
                  <input type="checkbox" v-model="carsInMaintenanceFilters.includeOverdue">
                  Просрочен техосмотр
                </label>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Фильтры для отчета по популярным моделям -->
        <div v-if="selectedReport === 'popular_cars'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item">
              <label>Дата начала:</label>
              <input type="date" v-model="popularCarsFilters.startDate">
            </div>
            <div class="filter-item">
              <label>Дата окончания:</label>
              <input type="date" v-model="popularCarsFilters.endDate">
            </div>
            <div class="filter-item">
              <label>Категория:</label>
              <select v-model="popularCarsFilters.category">
                <option value="">Все категории</option>
                <option value="Эконом">Эконом</option>
                <option value="Бизнес">Бизнес</option>
                <option value="Премиум">Премиум</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- Фильтры для отчета по активным договорам -->
        <div v-if="selectedReport === 'active_contracts'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item">
              <label>Сортировать по:</label>
              <select v-model="activeContractsFilters.sortBy">
                <option value="end_date">Дата окончания</option>
                <option value="start_date">Дата начала</option>
                <option value="client">Клиент</option>
                <option value="car">Автомобиль</option>
              </select>
            </div>
            <div class="filter-item">
              <label>Клиент:</label>
              <select v-model="activeContractsFilters.clientId">
                <option value="">Все клиенты</option>
                <option v-for="client in clients" :key="client.ID_клиента" :value="client.ID_клиента">{{ client.ФИО }}</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- Фильтры для отчета по завершенным договорам -->
        <div v-if="selectedReport === 'completed_contracts'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item">
              <label>Период:</label>
              <select v-model="completedContractsFilters.period">
                <option value="month">Месяц</option>
                <option value="quarter">Квартал</option>
                <option value="year">Год</option>
                <option value="custom">Указать даты</option>
              </select>
            </div>
            <div v-if="completedContractsFilters.period === 'custom'" class="filter-item">
              <label>Дата начала:</label>
              <input type="date" v-model="completedContractsFilters.startDate">
            </div>
            <div v-if="completedContractsFilters.period === 'custom'" class="filter-item">
              <label>Дата окончания:</label>
              <input type="date" v-model="completedContractsFilters.endDate">
            </div>
          </div>
        </div>
        
        <!-- Фильтры для отчета по просроченным платежам -->
        <div v-if="selectedReport === 'overdue_payments'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item">
              <label>Минимальная просрочка (дней):</label>
              <input type="number" v-model="overduePaymentsFilters.minDays" min="1">
            </div>
            <div class="filter-item">
              <label>Сортировать по:</label>
              <select v-model="overduePaymentsFilters.sortBy">
                <option value="days">Дням просрочки</option>
                <option value="amount">Сумме</option>
                <option value="client">Клиенту</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- Фильтры для отчета по доходам -->
        <div v-if="selectedReport === 'revenue'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item">
              <label>Период:</label>
              <select v-model="revenueFilters.period">
                <option value="month">Месяц</option>
                <option value="quarter">Квартал</option>
                <option value="year">Год</option>
                <option value="custom">Указать даты</option>
              </select>
            </div>
            <div v-if="revenueFilters.period === 'custom'" class="filter-item">
              <label>Дата начала:</label>
              <input type="date" v-model="revenueFilters.startDate">
            </div>
            <div v-if="revenueFilters.period === 'custom'" class="filter-item">
              <label>Дата окончания:</label>
              <input type="date" v-model="revenueFilters.endDate">
            </div>
          </div>
        </div>
        
        <!-- Фильтры для отчета по популярным услугам -->
        <div v-if="selectedReport === 'popular_services'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item">
              <label>Дата начала:</label>
              <input type="date" v-model="popularServicesFilters.startDate">
            </div>
            <div class="filter-item">
              <label>Дата окончания:</label>
              <input type="date" v-model="popularServicesFilters.endDate">
            </div>
          </div>
        </div>
        
        <!-- Фильтры для отчета по страховкам -->
        <div v-if="selectedReport === 'insurances'" class="report-filters">
          <h3>Фильтры:</h3>
          <div class="filters-grid">
            <div class="filter-item">
              <label>Тип страховки:</label>
              <select v-model="insuranceReportFilters.type">
                <option value="">Все типы</option>
                <option value="ОСАГО">ОСАГО</option>
                <option value="КАСКО">КАСКО</option>
              </select>
            </div>
            <div class="filter-item">
              <label>Максимальная сумма покрытия:</label>
              <input type="number" v-model="insuranceReportFilters.maxCoverage" min="0">
            </div>
            <div class="filter-item">
              <label>Статус:</label>
              <select v-model="insuranceReportFilters.status">
                <option value="">Все</option>
                <option value="active">Действующие</option>
                <option value="expired">Просроченные</option>
              </select>
            </div>
            <div class="filter-item">
              <label>Сортировка по стоимости:</label>
              <select v-model="insuranceReportFilters.priceSort">
                <option value="">Без сортировки</option>
                <option value="asc">По возрастанию</option>
                <option value="desc">По убыванию</option>
              </select>
            </div>
          </div>
        </div>
        
        <button @click="generateReport" class="generate-button">Сформировать отчет</button>
      </div>
      
      <!-- Результат отчета -->
      <div v-if="reportData && (Array.isArray(reportData) ? reportData.length > 0 : Object.keys(reportData).length > 0)" class="report-results">
        <h3>Результаты:</h3>
        
        <!-- Отчет по штрафам -->
        <table v-if="selectedReport === 'fines' && reportData.length">
          <thead>
            <tr>
              <th>ID договора</th>
              <th>Клиент</th>
              <th>Период договора</th>
              <th>Штраф</th>
              <th>Стоимость штрафа</th>
              <th>Количество</th>
              <th>Итого</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in reportData" :key="index">
              <td>{{ item.ID_договора }}</td>
              <td>{{ item.Клиент }}</td>
              <td>{{ formatDate(item.Дата_договора_начало) }} - {{ formatDate(item.Дата_договора_конец) }}</td>
              <td>{{ item.Штраф }}</td>
              <td>{{ item.Стоимость_штрафа }} ₽</td>
              <td>{{ item.Количество }}</td>
              <td>{{ item.Итого }} ₽</td>
            </tr>
          </tbody>
        </table>
        
        <!-- Отчет по автомобилям -->
        <table v-if="selectedReport === 'cars' && Array.isArray(reportData) && reportData.length">
          <thead>
            <tr>
              <th>ID</th>
              <th>Марка/Модель</th>
              <th>Год выпуска</th>
              <th>Категория</th>
              <th>Стоимость</th>
              <th>Статус</th>
              <th>Текущий арендатор</th>
              <th>Дата возврата</th>
              <th>Дата техосмотра</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in reportData" :key="index">
              <td>{{ item.ID_автомобиля }}</td>
              <td>{{ item.Марка }} {{ item.Модель }}</td>
              <td>{{ item.Год_выпуска }}</td>
              <td>{{ item.Категория }}</td>
              <td>{{ item.Стоимость }} ₽</td>
              <td>{{ item.Статус_авто }}</td>
              <td>{{ item.Текущий_арендатор || '-' }}</td>
              <td>{{ item.Дата_возврата ? formatDate(item.Дата_возврата) : '-' }}</td>
              <td>{{ formatDate(item.Дата_техосмотра) }}</td>
            </tr>
          </tbody>
        </table>
        
        <!-- Отчет по клиентам -->
        <table v-if="selectedReport === 'clients' && Array.isArray(reportData) && reportData.length">
          <thead>
            <tr>
              <th>ID</th>
              <th>ФИО</th>
              <th>Email</th>
              <th>Кол-во договоров</th>
              <th>Сумма договоров</th>
              <th>Сумма штрафов</th>
              <th>Итого</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in reportData" :key="index">
              <td>{{ item.ID_клиента }}</td>
              <td>{{ item.ФИО }}</td>
              <td>{{ item.email }}</td>
              <td>{{ item.Количество_договоров }}</td>
              <td>{{ item.Общая_сумма_договоров }} ₽</td>
              <td>{{ item.Общая_сумма_штрафов }} ₽</td>
              <td>{{ item.Итого }} ₽</td>
            </tr>
          </tbody>
        </table>
        
        <!-- Отчет по активным клиентам -->
        <div v-if="selectedReport === 'active_clients' && Array.isArray(reportData) && reportData && reportData.length">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>ФИО</th>
                <th>Email</th>
                <th>Телефоны</th>
                <th>Количество активных договоров</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in reportData || []" :key="index">
                <td>{{ item.ID_клиента }}</td>
                <td>{{ item.ФИО }}</td>
                <td>{{ item.email }}</td>
                <td>
                  <div v-for="(phone, phoneIndex) in item.Телефоны || []" :key="phoneIndex">
                    {{ phone.Номер }} ({{ phone.Тип }})
                  </div>
                </td>
                <td>{{ item.Количество_активных_договоров }}</td>
                <td>
                  <button @click="viewClientHistory(item.ID_клиента)" class="btn-view">История клиента</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Отчет по клиентам с просрочками -->
        <div v-if="selectedReport === 'overdue_clients' && Array.isArray(reportData) && reportData.length">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>ФИО</th>
                <th>Email</th>
                <th>Телефоны</th>
                <th>Просроченные платежи</th>
                <th>Неоплаченные штрафы</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in reportData" :key="index">
                <td>{{ item.ID_клиента }}</td>
                <td>{{ item.ФИО }}</td>
                <td>{{ item.email }}</td>
                <td>
                  <div v-for="(phone, phoneIndex) in item.Телефоны" :key="phoneIndex">
                    {{ phone.Номер }} ({{ phone.Тип }})
                  </div>
                </td>
                <td @click="showPaymentsDetails(item)" :class="{ 'clickable-cell': item.Просроченные_платежи.length > 0 }">
                  {{ item.Просроченные_платежи.length }}
                </td>
                <td @click="showFinesDetails(item)" :class="{ 'clickable-cell': item.Неоплаченные_штрафы.length > 0 }">
                  {{ item.Неоплаченные_штрафы.length }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Отчет по автомобилям на техобслуживании -->
        <div v-if="selectedReport === 'cars_in_maintenance' && !Array.isArray(reportData) && Object.keys(reportData).length">
          <div v-if="reportData.На_обслуживании && reportData.На_обслуживании.length" class="report-section">
            <h3>Автомобили на обслуживании</h3>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Марка/Модель</th>
                  <th>Год выпуска</th>
                  <th>Категория</th>
                  <th>Дата техосмотра</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(car, index) in reportData.На_обслуживании" :key="'maintenance-'+index">
                  <td>{{ car.ID_автомобиля }}</td>
                  <td>{{ car.Марка }} {{ car.Модель }}</td>
                  <td>{{ car.Год_выпуска }}</td>
                  <td>{{ car.Категория }}</td>
                  <td>{{ formatDate(car.Дата_техосмотра) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div v-if="reportData.Просрочен_техосмотр && reportData.Просрочен_техосмотр.length" class="report-section">
            <h3>Просрочен техосмотр</h3>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Марка/Модель</th>
                  <th>Год выпуска</th>
                  <th>Категория</th>
                  <th>Дата техосмотра</th>
                  <th>Просрочено дней</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(car, index) in reportData.Просрочен_техосмотр" :key="'overdue-'+index">
                  <td>{{ car.ID_автомобиля }}</td>
                  <td>{{ car.Марка }} {{ car.Модель }}</td>
                  <td>{{ car.Год_выпуска }}</td>
                  <td>{{ car.Категория }}</td>
                  <td>{{ formatDate(car.Дата_техосмотра) }}</td>
                  <td>{{ car.Просрочено_дней }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Отчет по активным договорам -->
        <div v-if="selectedReport === 'active_contracts' && Array.isArray(reportData) && reportData.length">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Клиент</th>
                <th>Автомобиль</th>
                <th>Период</th>
                <th>Осталось дней</th>
                <th>Стоимость</th>
                <th>Статус оплаты</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(contract, index) in reportData" :key="index">
                <td>{{ contract.ID_договора }}</td>
                <td>{{ contract.Клиент }}</td>
                <td>{{ contract.Автомобиль }}</td>
                <td>{{ formatDate(contract.Дата_начала) }} - {{ formatDate(contract.Дата_окончания) }}</td>
                <td>{{ contract.Осталось_дней }}</td>
                <td>{{ contract.Стоимость }} ₽</td>
                <td>{{ contract.Статус_оплаты }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Отчет по завершенным договорам -->
        <div v-if="selectedReport === 'completed_contracts' && !Array.isArray(reportData) && reportData.Период">
          <div class="report-summary">
            <h3>Сводная информация</h3>
            <p><strong>Период:</strong> {{ reportData.Период.Начало }} - {{ reportData.Период.Конец }}</p>
            <p><strong>Количество договоров:</strong> {{ reportData.Количество_договоров }}</p>
            <p><strong>Общая выручка:</strong> {{ reportData.Общая_выручка }} ₽</p>
          </div>
          
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Клиент</th>
                <th>Автомобиль</th>
                <th>Период</th>
                <th>Длительность (дней)</th>
                <th>Стоимость</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(contract, index) in reportData.Договоры" :key="index">
                <td>{{ contract.ID_договора }}</td>
                <td>{{ contract.Клиент }}</td>
                <td>{{ contract.Автомобиль }}</td>
                <td>{{ formatDate(contract.Дата_начала) }} - {{ formatDate(contract.Дата_окончания) }}</td>
                <td>{{ contract.Длительность_дней }}</td>
                <td>{{ contract.Стоимость }} ₽</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Отчет по просроченным платежам -->
        <div v-if="selectedReport === 'overdue_payments'">
          <table>
            <thead>
              <tr>
                <th>ID договора</th>
                <th>Клиент</th>
                <th>Контакты</th>
                <th>Автомобиль</th>
                <th>Период аренды</th>
                <th>Просрочено дней</th>
                <th>Стоимость</th>
                <th>Способ оплаты</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(payment, index) in reportData" :key="index">
                <td>{{ payment.ID_договора }}</td>
                <td>{{ payment.Клиент }}</td>
                <td>{{ payment.email }}<br>{{ payment.Телефоны.join(', ') }}</td>
                <td>{{ payment.Автомобиль }}</td>
                <td>{{ formatDate(payment.Дата_начала) }} - {{ formatDate(payment.Дата_окончания) }}</td>
                <td>{{ payment.Просрочено_дней }}</td>
                <td>{{ payment.Стоимость }} ₽</td>
                <td>{{ payment.Способ_оплаты }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Отчет по доходам -->
        <div v-if="selectedReport === 'revenue'">
          <div class="report-summary">
            <h3>Сводная информация</h3>
            <p><strong>Период:</strong> {{ reportData.Период.Начало }} - {{ reportData.Период.Конец }}</p>
            <p><strong>Количество договоров:</strong> {{ reportData.Количество_договоров }}</p>
            <p><strong>Общая выручка:</strong> {{ reportData.Общая_выручка }} ₽</p>
          </div>
          
          <div class="report-section">
            <h3>Выручка по категориям автомобилей</h3>
            <table>
              <thead>
                <tr>
                  <th>Категория</th>
                  <th>Сумма</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in reportData.Выручка_по_категориям" :key="'cat-'+index">
                  <td>{{ item.Категория }}</td>
                  <td>{{ item.Сумма }} ₽</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div class="report-section">
            <h3>Выручка по способам оплаты</h3>
            <table>
              <thead>
                <tr>
                  <th>Способ оплаты</th>
                  <th>Сумма</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in reportData.Выручка_по_способам_оплаты" :key="'payment-'+index">
                  <td>{{ item.Способ_оплаты }}</td>
                  <td>{{ item.Сумма }} ₽</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Отчет по популярным услугам -->
        <div v-if="selectedReport === 'popular_services'">
          <div class="report-summary">
            <h3>Сводная информация</h3>
            <p v-if="reportData.Период"><strong>Период:</strong> {{ reportData.Период.Начало }} - {{ reportData.Период.Конец }}</p>
            <p v-else><strong>Период:</strong> Данные недоступны</p>
            <p><strong>Количество договоров:</strong> {{ reportData.Общее_количество_договоров || 0 }}</p>
            <p><strong>Общая выручка от услуг:</strong> {{ reportData.Общая_выручка_от_услуг || 0 }} ₽</p>
          </div>
          
          <table v-if="reportData.Услуги && reportData.Услуги.length">
            <thead>
              <tr>
                <th>ID</th>
                <th>Название услуги</th>
                <th>Стоимость</th>
                <th>Количество договоров</th>
                <th>Общее количество</th>
                <th>Выручка</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(service, index) in reportData.Услуги" :key="index">
                <td>{{ service.ID_услуги }}</td>
                <td>{{ service.Название }}</td>
                <td>{{ service.Стоимость }} ₽</td>
                <td>{{ service.Количество_договоров }}</td>
                <td>{{ service.Общее_количество }}</td>
                <td>{{ service.Выручка }} ₽</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="no-data">Нет данных для отображения</p>
        </div>
        
        <!-- Отчет по популярным автомобилям -->
        <div v-if="selectedReport === 'popular_cars' && Array.isArray(reportData) && reportData.length">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Марка/Модель</th>
                <th>Категория</th>
                <th>Количество аренд</th>
                <th>Стоимость в день</th>
                <th>Общая выручка</th>
                <th>Средняя продолжительность (дней)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(car, index) in reportData" :key="index">
                <td>{{ car.ID_автомобиля }}</td>
                <td>{{ car.Марка }} {{ car.Модель }}</td>
                <td>{{ car.Категория }}</td>
                <td>{{ car.Количество_аренд }}</td>
                <td>{{ car.Стоимость_в_день }} ₽</td>
                <td>{{ car.Общая_выручка }} ₽</td>
                <td>{{ car.Средняя_продолжительность }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Отчет по страховкам -->
        <div v-if="selectedReport === 'insurances' && Array.isArray(reportData) && reportData.length">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Автомобиль</th>
                <th>Тип страховки</th>
                <th>Максимальная сумма покрытия</th>
                <th>Номер полиса</th>
                <th>Дата начала</th>
                <th>Дата окончания</th>
                <th>Стоимость</th>
                <th>Статус</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in reportData" :key="index">
                <td>{{ item.ID_страховки }}</td>
                <td>{{ item.Автомобиль }}</td>
                <td>{{ item.Тип_страховки }}</td>
                <td>{{ item.Максимум_покрытия }} ₽</td>
                <td>{{ item.Номер_полиса }}</td>
                <td>{{ formatDate(item.Дата_начала) }}</td>
                <td>{{ formatDate(item.Дата_окончания) }}</td>
                <td>{{ item.Стоимость }} ₽</td>
                <td>{{ item.Просрочена ? 'Просрочена' : 'Действующая' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для добавления штрафа -->
    <div v-if="showAddFineModal" class="modal">
      <div class="modal-content">
        <h2>Добавить штраф</h2>
        <div>
          <p><strong>Договор №:</strong> {{ selectedContract.ID_договора }}</p>
          <p><strong>Клиент:</strong> {{ selectedContract.Клиент }}</p>
          <p><strong>Автомобиль:</strong> {{ selectedContract.Автомобиль }}</p>
        </div>
        
        <div class="form-group">
          <label>Тип штрафа:</label>
          <select v-model="newFine.ID_штрафа" required class="form-input">
            <option v-for="fine in fines" :key="fine.ID_штрафа" :value="fine.ID_штрафа">
              {{ fine.Название }} ({{ fine.Стоимость }} ₽)
            </option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Количество:</label>
          <input type="number" v-model="newFine.Количество" min="1" required class="form-input">
        </div>
        
        <div class="modal-buttons">
          <button @click="addFine" class="save-button">Добавить</button>
          <button @click="closeAddFineModal" class="cancel-button">Отмена</button>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для добавления автомобиля -->
    <div v-if="showAddCarModal" class="modal">
      <div class="modal-content add-car-modal">
        <h2>Добавить автомобиль</h2>
        
        <div class="form-group">
          <label>Марка:</label>
          <input type="text" v-model="newCar.Марка" required class="form-input">
        </div>
        
        <div class="form-group">
          <label>Модель:</label>
          <input type="text" v-model="newCar.Модель" required class="form-input">
        </div>
        
        <div class="form-group">
          <label>Год выпуска:</label>
          <input type="number" v-model="newCar.Год_выпуска" required class="form-input">
        </div>
        
        <div class="form-group">
          <label>Категория:</label>
          <select v-model="newCar.Категория" required class="form-input">
            <option value="Эконом">Эконом</option>
            <option value="Бизнес">Бизнес</option>
            <option value="Премиум">Премиум</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Стоимость (в день):</label>
          <input type="number" v-model="newCar.Стоимость" required class="form-input">
        </div>
        
        <div class="form-group">
          <label>Статус:</label>
          <select v-model="newCar.Статус_авто" required class="form-input">
            <option value="Доступен">Доступен</option>
            <option value="В аренде">В аренде</option>
            <option value="На обслуживании">На обслуживании</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Дата техосмотра:</label>
          <input type="date" v-model="newCar.Дата_техосмотра" class="form-input">
        </div>
        
        <div class="form-group">
          <label>Ссылка на изображение:</label>
          <input type="text" v-model="newCar.image" class="form-input">
        </div>
        
        <div class="modal-buttons">
          <button @click="addCar" class="save-button">Добавить</button>
          <button @click="showAddCarModal = false" class="cancel-button">Отмена</button>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для добавления типа штрафа -->
    <div v-if="showAddFineTypeModal" class="modal">
      <div class="modal-content">
        <h2>Добавить тип штрафа</h2>
        
        <div class="form-group">
          <label>Название:</label>
          <input 
            type="text" 
            v-model="newFineType.Название" 
            required
            class="form-input"
          >
        </div>
        
        <div class="form-group">
          <label>Стоимость (₽):</label>
          <input 
            type="number" 
            v-model="newFineType.Стоимость" 
            required
            min="0"
            class="form-input"
          >
        </div>
        
        <div class="modal-buttons">
          <button @click="addFineType" class="save-button">Добавить</button>
          <button @click="showAddFineTypeModal = false" class="cancel-button">Отмена</button>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для добавления услуги -->
    <div v-if="showAddServiceModal" class="modal">
      <div class="modal-content">
        <h2>Добавить услугу</h2>
        
        <div class="form-group">
          <label>Название:</label>
          <input 
            type="text" 
            v-model="newService.Название" 
            required
            class="form-input"
          >
        </div>
        
        <div class="form-group">
          <label>Стоимость (₽):</label>
          <input 
            type="number" 
            v-model="newService.Стоимость" 
            required
            min="0"
            class="form-input"
          >
        </div>
        
        <div class="modal-buttons">
          <button @click="addService" class="save-button">Добавить</button>
          <button @click="showAddServiceModal = false" class="cancel-button">Отмена</button>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для добавления сотрудника -->
    <div v-if="showAddEmployeeModal" class="modal">
      <div class="modal-content add-employee-modal">
        <h2>Добавить сотрудника</h2>
        
        <div class="form-group">
          <label>ФИО:</label>
          <input 
            type="text" 
            v-model="newEmployee.ФИО_с" 
            required
            class="form-input"
          >
        </div>
        
        <div class="form-group">
          <label>Должность:</label>
          <input 
            type="text" 
            v-model="newEmployee.Должность" 
            required
            class="form-input"
          >
        </div>
        
        <div class="form-group">
          <label>Телефон:</label>
          <input 
            type="text" 
            v-model="newEmployee.Телефон_с" 
            required
            class="form-input"
          >
        </div>
        
        <div class="form-group">
          <label>Email:</label>
          <input 
            type="email" 
            v-model="newEmployee.email" 
            required
            class="form-input"
          >
        </div>
        
        <div class="form-group">
          <label>Оклад (₽):</label>
          <input 
            type="number" 
            v-model="newEmployee.Оклад" 
            required
            min="0"
            class="form-input"
          >
        </div>
        
        <div class="form-group">
          <label>Пароль:</label>
          <input 
            type="password" 
            v-model="newEmployee.Пароль" 
            required
            class="form-input"
          >
        </div>
        
        <div class="modal-buttons">
          <button @click="addEmployee" class="save-button">Добавить</button>
          <button @click="showAddEmployeeModal = false" class="cancel-button">Отмена</button>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для просроченных платежей -->
    <div v-if="showPaymentsModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Просроченные платежи клиента: {{ currentClientName }}</h3>
          <span class="close" @click="showPaymentsModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <table>
            <thead>
              <tr>
                <th>ID договора</th>
                <th>Период аренды</th>
                <th>Статус оплаты</th>
                <th>Просрочено дней</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(payment, index) in currentPayments" :key="index">
                <td>{{ payment.ID_договора }}</td>
                <td>{{ payment.Дата_начала }} - {{ payment.Дата_окончания }}</td>
                <td>{{ payment.Статус_оплаты }}</td>
                <td>{{ payment.Просрочено_дней }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для неоплаченных штрафов -->
    <div v-if="showFinesModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Неоплаченные штрафы клиента: {{ currentClientName }}</h3>
          <span class="close" @click="showFinesModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <table>
            <thead>
              <tr>
                <th>ID договора</th>
                <th>Период аренды</th>
                <th>Название штрафа</th>
                <th>Количество</th>
                <th>Стоимость</th>
                <th>Итого</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(fine, index) in currentFines" :key="index">
                <td>{{ fine.ID_договора }}</td>
                <td>{{ fine.Срок_аренды }}</td>
                <td>{{ fine.Название }}</td>
                <td>{{ fine.Количество }}</td>
                <td>{{ fine.Стоимость }} ₽</td>
                <td>{{ fine.Итого }} ₽</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для документов клиента -->
    <div v-if="showClientDocumentsModal" class="modal">
      <div class="modal-content documents-modal">
        <div class="modal-header">
          <h3>Документы клиента: {{ selectedClientName }}</h3>
          <span class="close" @click="showClientDocumentsModal = false">&times;</span>
        </div>
        <div class="modal-body">
          <div v-if="clientDocuments" class="documents-container">
            <div class="document-section passport-section">
              <h4>Паспорт</h4>
              <div class="document-details">
                <p><strong>Серия и номер:</strong> {{ clientDocuments.паспорт?.Серия_Номер || 'Не указано' }}</p>
                <p><strong>Дата выдачи:</strong> {{ formatDate(clientDocuments.паспорт?.Дата_выдачи) }}</p>
                <p><strong>Срок действия:</strong> {{ formatDate(clientDocuments.паспорт?.Срок_действия) }}</p>
                <p><strong>Кем выдан:</strong> {{ clientDocuments.паспорт?.Кем_выдан || 'Не указано' }}</p>
                <p><strong>Код подразделения:</strong> {{ clientDocuments.паспорт?.Код_подразделения || 'Не указано' }}</p>
              </div>
            </div>
            
            <div class="document-section license-section">
              <h4>Водительское удостоверение</h4>
              <div class="document-details">
                <p><strong>Номер:</strong> {{ clientDocuments.вод_удостоверение?.Номер || 'Не указано' }}</p>
                <p><strong>Дата выдачи:</strong> {{ formatDate(clientDocuments.вод_удостоверение?.Дата_выдачи) }}</p>
                <p><strong>Срок действия:</strong> {{ formatDate(clientDocuments.вод_удостоверение?.Срок_действия) }}</p>
                <p><strong>Место выдачи:</strong> {{ clientDocuments.вод_удостоверение?.Место_выдачи || 'Не указано' }}</p>
              </div>
            </div>
          </div>
          <div v-else class="no-documents">
            <p>Документы не найдены</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'EmployeeCabinet',
  data() {
    return {
      activeTab: 'clients',
      clients: [],
      contracts: [],
      fines: [],
      cars: [],
      bookings: [],
      services: [],
      employees: [],
      selectedReport: '',
      reportData: {}, // Инициализируем как пустой объект
      
      // Фильтры для отчетов
      fineReportFilters: {
        startDate: '',
        endDate: '',
        clientId: '',
        paid: ''
      },
      carReportFilters: {
        yearFrom: '',
        yearTo: '',
        category: ''
      },
      clientReportFilters: {
        gender: '',
        bookingsFrom: ''
      },
      profitReportFilters: {
        period: 'month',
        startDate: '',
        endDate: ''
      },
      overdueClientsFilters: {
        overdueCount: '',
        type: 'all'
      },
      insuranceReportFilters: {
        type: '',
        maxCoverage: '',
        status: '',
        priceSort: ''
      },
      
      // Данные для модальных окон
      showPaymentsModal: false,
      showFinesModal: false,
      currentPayments: [],
      currentFines: [],
      currentClientName: '',
      
      showAddFineModal: false,
      showAddCarModal: false,
      showAddFineTypeModal: false,
      showAddServiceModal: false,
      showAddEmployeeModal: false,
      
      // Данные для новых элементов
      selectedContract: {},
      newFine: {
        ID_договора: null,
        ID_штрафа: null,
        Количество: 1
      },
      newCar: {
        Марка: '',
        Модель: '',
        Год_выпуска: new Date().getFullYear(),
        Категория: 'Эконом',
        Стоимость: 0,
        Статус_авто: 'Доступен',
        Дата_техосмотра: new Date().toISOString().split('T')[0],
        image: ''
      },
      newFineType: {
        Название: '',
        Стоимость: 0
      },
      newService: {
        Название: '',
        Стоимость: 0
      },
      newEmployee: {
        ФИО_с: '',
        Должность: '',
        Телефон_с: '',
        email: '',
        Оклад: 0,
        Пароль: ''
      },
      overduePaymentsFilters: {
        minDays: 1,
        sortBy: 'days'
      },
      revenueFilters: {
        period: 'month',
        startDate: '',
        endDate: ''
      },
      popularServicesFilters: {
        startDate: '',
        endDate: ''
      },
      carsInMaintenanceFilters: {
        includeMaintenance: true,
        includeOverdue: true
      },
      popularCarsFilters: {
        startDate: '',
        endDate: '',
        category: ''
      },
      activeContractsFilters: {
        sortBy: 'end_date',
        clientId: ''
      },
      completedContractsFilters: {
        period: 'month',
        startDate: '',
        endDate: ''
      },
      
      // Для клиентов и документов
      showClientDocumentsModal: false,
      selectedClientName: '',
      selectedClientId: null,
      clientDocuments: null
    }
  },
  created() {
    this.fetchClients()
    this.fetchContracts()
    this.fetchFines()
    this.fetchContractFines()
    this.fetchCars()
    this.fetchServices()
    this.fetchEmployees()
  },
  methods: {
    setActiveTab(tab) {
      this.activeTab = tab
    },
    
    async fetchClients() {
      try {
        const response = await axios.get('/api/employee/clients')
        this.clients = response.data
      } catch (error) {
        console.error('Ошибка при получении списка клиентов:', error)
        alert('Ошибка при получении списка клиентов')
      }
    },
    
    async fetchContracts() {
      try {
        const response = await axios.get('/api/employee/contracts')
        this.contracts = response.data
      } catch (error) {
        console.error('Ошибка при получении списка договоров:', error)
        alert('Ошибка при получении списка договоров')
      }
    },
    
    async fetchFines() {
      try {
        const response = await axios.get('/api/employee/fines')
        this.fines = response.data
        console.log(`Получено типов штрафов: ${this.fines.length}`)
      } catch (error) {
        console.error('Ошибка при получении списка штрафов:', error)
        
        // Показываем более подробную информацию об ошибке
        let errorMessage = 'Ошибка при получении списка штрафов'
        if (error.response) {
          // Если есть ответ сервера с ошибкой
          errorMessage += error.response.data.error 
            ? `: ${error.response.data.error}` 
            : ` (${error.response.status})`
        } else if (error.request) {
          // Если сервер не ответил
          errorMessage += ': Нет ответа от сервера'
        } else {
          // Другие ошибки
          errorMessage += `: ${error.message}`
        }
        
        alert(errorMessage)
      }
    },
    
    async fetchContractFines() {
      try {
        const response = await axios.get('/api/employee/contract_fines')
        this.contractFines = response.data
      } catch (error) {
        // Тихо обрабатываем ошибку без вывода сообщений
        this.contractFines = []
      }
    },
    
    async fetchCars() {
      try {
        const response = await axios.get('/api/employee/cars')
        this.cars = response.data
      } catch (error) {
        console.error('Ошибка при получении списка автомобилей:', error)
        alert('Ошибка при получении списка автомобилей')
      }
    },
    
    async fetchServices() {
      try {
        const response = await axios.get('/api/employee/services')
        this.services = response.data
      } catch (error) {
        console.error('Ошибка при получении списка услуг:', error)
        alert('Ошибка при получении списка услуг')
      }
    },
    
    async fetchEmployees() {
      try {
        const response = await axios.get('/api/employee/employees')
        this.employees = response.data
      } catch (error) {
        console.error('Ошибка при получении списка сотрудников:', error)
        alert('Ошибка при получении списка сотрудников')
      }
    },
    
    openAddFineModal(contract) {
      this.selectedContract = contract
      this.newFine.ID_договора = contract.ID_договора
      this.showAddFineModal = true
    },
    
    closeAddFineModal() {
      this.showAddFineModal = false
      this.selectedContract = {}
      this.newFine = {
        ID_договора: null,
        ID_штрафа: null,
        Количество: 1
      }
    },
    
    async addFine() {
      try {
        // Убедимся, что количество - это число
        this.newFine.Количество = parseInt(this.newFine.Количество, 10) || 1;
        
        // Получаем ID сотрудника из localStorage
        const employeeInfo = JSON.parse(localStorage.getItem('employee_info') || '{}');
        this.newFine.ID_сотрудника = employeeInfo.ID_сотрудника;
        
        await axios.post('/api/employee/add_fine', this.newFine)
        alert('Штраф успешно добавлен')
        this.closeAddFineModal()
        this.fetchContractFines() // Обновляем список штрафов
      } catch (error) {
        console.error('Ошибка при добавлении штрафа:', error)
        alert('Ошибка при добавлении штрафа')
      }
    },
    
    async addCar() {
      try {
        await axios.post('/api/employee/add_car', this.newCar)
        alert('Автомобиль успешно добавлен')
        this.showAddCarModal = false
        this.newCar = {
          Марка: '',
          Модель: '',
          Год_выпуска: new Date().getFullYear(),
          Категория: 'Эконом',
          Стоимость: 0,
          Статус_авто: 'Доступен',
          Дата_техосмотра: new Date().toISOString().split('T')[0],
          image: ''
        }
        this.fetchCars() // Обновляем список автомобилей
      } catch (error) {
        console.error('Ошибка при добавлении автомобиля:', error)
        alert('Ошибка при добавлении автомобиля')
      }
    },
    
    async addFineType() {
      try {
        if (!this.newFineType.Название || !this.newFineType.Стоимость) {
          alert('Пожалуйста, заполните все поля')
          return
        }
        
        await this.$axios.post('/api/employee/add_fine_type', {
          Название: this.newFineType.Название,
          Стоимость: Number(this.newFineType.Стоимость)
        })
        
        this.showAddFineTypeModal = false
        this.newFineType = {
          Название: '',
          Стоимость: 0
        }
        
        // Обновляем список типов штрафов
        await this.fetchFines()
      } catch (error) {
        console.error('Ошибка при добавлении типа штрафа:', error)
        alert('Не удалось добавить тип штрафа')
      }
    },
    
    async addService() {
      try {
        if (!this.newService.Название || !this.newService.Стоимость) {
          alert('Пожалуйста, заполните все поля')
          return
        }
        
        await axios.post('/api/employee/add_service', {
          Название: this.newService.Название,
          Стоимость: Number(this.newService.Стоимость)
        })
        
        alert('Услуга успешно добавлена')
        this.showAddServiceModal = false
        this.newService = {
          Название: '',
          Стоимость: 0
        }
        
        // Обновляем список услуг
        await this.fetchServices()
      } catch (error) {
        console.error('Ошибка при добавлении услуги:', error)
        alert('Не удалось добавить услугу')
      }
    },
    
    async addEmployee() {
      try {
        if (!this.newEmployee.ФИО_с || !this.newEmployee.Должность || 
            !this.newEmployee.email || !this.newEmployee.Пароль) {
          alert('Пожалуйста, заполните все обязательные поля')
          return
        }
        
        await axios.post('/api/employee/add_employee', this.newEmployee)
        
        alert('Сотрудник успешно добавлен')
        this.showAddEmployeeModal = false
        this.newEmployee = {
          ФИО_с: '',
          Должность: '',
          Телефон_с: '',
          email: '',
          Оклад: 0,
          Пароль: ''
        }
        
        // Обновляем список сотрудников
        await this.fetchEmployees()
      } catch (error) {
        console.error('Ошибка при добавлении сотрудника:', error)
        alert('Не удалось добавить сотрудника')
      }
    },
    
    async generateReport() {
      try {
        // Очистим старые данные
        this.reportData = Array.isArray(this.reportData) ? [] : {};
        
        let url = ''
        let params = {}
        
        if (this.selectedReport === 'fines') {
          url = '/api/employee/reports/fines'
          if (this.fineReportFilters.startDate) {
            params.start_date = this.fineReportFilters.startDate
          }
          if (this.fineReportFilters.endDate) {
            params.end_date = this.fineReportFilters.endDate
          }
          if (this.fineReportFilters.clientId) {
            params.client_id = this.fineReportFilters.clientId
          }
        } else if (this.selectedReport === 'cars') {
          url = '/api/employee/reports/cars'
          if (this.carReportFilters.status) {
            params.status = this.carReportFilters.status
          }
          if (this.carReportFilters.category) {
            params.category = this.carReportFilters.category
          }
          if (this.carReportFilters.yearFrom) {
            params.year_from = this.carReportFilters.yearFrom
          }
          if (this.carReportFilters.yearTo) {
            params.year_to = this.carReportFilters.yearTo
          }
        } else if (this.selectedReport === 'clients') {
          url = '/api/employee/reports/clients'
          if (this.clientReportFilters.gender) {
            params.gender = this.clientReportFilters.gender
          }
          if (this.clientReportFilters.bookingsFrom) {
            params.bookings_from = this.clientReportFilters.bookingsFrom
          }
        } else if (this.selectedReport === 'bookings') {
          url = '/api/employee/reports/bookings'
          if (this.bookingReportFilters.startDate) {
            params.start_date = this.bookingReportFilters.startDate
          }
          if (this.bookingReportFilters.endDate) {
            params.end_date = this.bookingReportFilters.endDate
          }
          if (this.bookingReportFilters.paymentMethod) {
            params.payment_method = this.bookingReportFilters.paymentMethod
          }
        } else if (this.selectedReport === 'profit') {
          url = '/api/employee/reports/profit'
          if (this.profitReportFilters.period) {
            params.period = this.profitReportFilters.period
          }
          if (this.profitReportFilters.startDate) {
            params.start_date = this.profitReportFilters.startDate
          }
          if (this.profitReportFilters.endDate) {
            params.end_date = this.profitReportFilters.endDate
          }
        } else if (this.selectedReport === 'overdue_clients') {
          url = '/api/employee/reports/overdue_clients'
          if (this.overdueClientsFilters.overdueCount) {
            params.overdue_count = Number(this.overdueClientsFilters.overdueCount)
          }
          if (this.overdueClientsFilters.type) {
            params.type = this.overdueClientsFilters.type
          }
        } else if (this.selectedReport === 'cars_in_maintenance') {
          url = '/api/employee/reports/cars_in_maintenance'
          // Явно передаем булевы значения чекбоксов
          params.include_maintenance = this.carsInMaintenanceFilters.includeMaintenance
          params.include_overdue = this.carsInMaintenanceFilters.includeOverdue
          
          console.log('[DEBUG] Отправка фильтров для cars_in_maintenance:', params)
        } else if (this.selectedReport === 'popular_cars') {
          url = '/api/employee/reports/popular_cars'
          if (this.popularCarsFilters.startDate) {
            params.start_date = this.popularCarsFilters.startDate
          }
          if (this.popularCarsFilters.endDate) {
            params.end_date = this.popularCarsFilters.endDate
          }
          if (this.popularCarsFilters.category) {
            params.category = this.popularCarsFilters.category
          }
        } else if (this.selectedReport === 'active_contracts') {
          url = '/api/employee/reports/active_contracts'
          if (this.activeContractsFilters.sortBy) {
            params.sort_by = this.activeContractsFilters.sortBy
          }
          if (this.activeContractsFilters.clientId) {
            params.client_id = this.activeContractsFilters.clientId
          }
          console.log('[DEBUG] Отправка запроса для активных договоров:', url, params)
        } else if (this.selectedReport === 'completed_contracts') {
          url = '/api/employee/reports/completed_contracts'
          if (this.completedContractsFilters.period) {
            params.period = this.completedContractsFilters.period
          }
          if (this.completedContractsFilters.startDate) {
            params.start_date = this.completedContractsFilters.startDate
          }
          if (this.completedContractsFilters.endDate) {
            params.end_date = this.completedContractsFilters.endDate
          }
        } else if (this.selectedReport === 'overdue_payments') {
          url = '/api/employee/reports/overdue_payments'
          if (this.overduePaymentsFilters.minDays) {
            params.min_days = this.overduePaymentsFilters.minDays
          }
          if (this.overduePaymentsFilters.sortBy) {
            params.sort_by = this.overduePaymentsFilters.sortBy
          }
        } else if (this.selectedReport === 'revenue') {
          url = '/api/employee/reports/revenue'
          if (this.revenueFilters.period) {
            params.period = this.revenueFilters.period
          }
          if (this.revenueFilters.startDate) {
            params.start_date = this.revenueFilters.startDate
          }
          if (this.revenueFilters.endDate) {
            params.end_date = this.revenueFilters.endDate
          }
        } else if (this.selectedReport === 'popular_services') {
          url = '/api/employee/reports/popular_services'
          if (this.popularServicesFilters.startDate) {
            params.start_date = this.popularServicesFilters.startDate
          }
          if (this.popularServicesFilters.endDate) {
            params.end_date = this.popularServicesFilters.endDate
          }
        } else if (this.selectedReport === 'insurances') {
          url = '/api/employee/reports/insurances'
          if (this.insuranceReportFilters.type) {
            params.type = this.insuranceReportFilters.type
          }
          if (this.insuranceReportFilters.maxCoverage) {
            params.max_coverage = this.insuranceReportFilters.maxCoverage
          }
          if (this.insuranceReportFilters.status) {
            params.status = this.insuranceReportFilters.status
          }
          if (this.insuranceReportFilters.priceSort) {
            params.price_sort = this.insuranceReportFilters.priceSort
          }
        }
        
        console.log(`Запрос отчета ${this.selectedReport}: ${url}`, params)
        
        try {
          const response = await axios.get(url, { params })
          console.log('Получены данные отчета:', response.data)
          this.reportData = response.data
        } catch (error) {
          console.error(`Ошибка при получении отчета ${this.selectedReport}:`, error)
          console.error('Дополнительная информация:', error.message)
          if (error.response) {
            console.error('Статус ответа:', error.response.status)
            console.error('Данные ответа:', error.response.data)
          }
          if (error.request) {
            console.error('Запрос был отправлен, но ответ не получен')
          }
          
          alert(`Ошибка при формировании отчета ${this.selectedReport}: ${error.message}`)
        }
      } catch (error) {
        console.error('Общая ошибка при формировании отчета:', error)
        alert('Ошибка при формировании отчета')
      }
    },
    formatDate(date) {
      console.log('Форматирование даты:', date, typeof date);
      if (!date) {
        return 'Не указана';
      }
      
      try {
        const formattedDate = new Date(date).toLocaleDateString('ru-RU');
        console.log('Отформатированная дата:', formattedDate);
        return formattedDate;
      } catch (error) {
        console.error('Ошибка форматирования даты:', error);
        return 'Ошибка формата';
      }
    },
    async updateCarStatus(carId, newStatus) {
      try {
        await axios.post('/api/employee/update_car_status', {
          ID_автомобиля: carId,
          Статус_авто: newStatus
        })
        alert('Статус автомобиля успешно обновлен')
        this.fetchCars() // Обновляем список автомобилей
      } catch (error) {
        console.error('Ошибка при обновлении статуса автомобиля:', error)
        alert('Ошибка при обновлении статуса автомобиля')
      }
    },
    async updateCarPrice(carId, newPrice) {
      try {
        await axios.post('/api/employee/update_car_price', {
          ID_автомобиля: carId,
          Стоимость: newPrice
        })
        alert('Стоимость автомобиля успешно обновлена')
        this.fetchCars() // Обновляем список автомобилей
      } catch (error) {
        console.error('Ошибка при обновлении стоимости автомобиля:', error)
        alert('Ошибка при обновлении стоимости автомобиля')
      }
    },
    async updateCarInspectionDate(carId, newDate) {
      try {
        await axios.post('/api/employee/update_car_inspection_date', {
          ID_автомобиля: carId,
          Дата_техосмотра: newDate
        })
        alert('Дата техосмотра автомобиля успешно обновлена')
        this.fetchCars() // Обновляем список автомобилей
      } catch (error) {
        console.error('Ошибка при обновлении даты техосмотра автомобиля:', error)
        alert('Ошибка при обновлении даты техосмотра автомобиля')
      }
    },
    async updateFinePrice(fineId, newPrice) {
      try {
        await axios.post('/api/employee/update_fine_price', {
          ID_штрафа: fineId,
          Стоимость: newPrice
        })
        alert('Стоимость штрафа успешно обновлена')
        this.fetchFines() // Обновляем список типов штрафов
      } catch (error) {
        console.error('Ошибка при обновлении стоимости штрафа:', error)
        alert('Ошибка при обновлении стоимости штрафа')
      }
    },
    async viewClientHistory(clientId) {
      try {
        this.selectedReport = 'client_history'
        const response = await axios.get(`/api/employee/reports/client_history/${clientId}`)
        this.reportData = response.data
      } catch (error) {
        console.error('Ошибка при получении истории клиента:', error)
        alert('Ошибка при получении истории клиента')
      }
    },
    showPaymentsDetails(item) {
      if (!item.Просроченные_платежи || item.Просроченные_платежи.length === 0) return;
      
      this.currentPayments = item.Просроченные_платежи;
      this.currentClientName = item.ФИО;
      this.showPaymentsModal = true;
    },
    showFinesDetails(item) {
      if (!item.Неоплаченные_штрафы || item.Неоплаченные_штрафы.length === 0) return;
      
      this.currentFines = item.Неоплаченные_штрафы;
      this.currentClientName = item.ФИО;
      this.showFinesModal = true;
    },
    async viewClientDocuments(clientId) {
      try {
        const response = await axios.get(`/api/employee/client_documents/${clientId}`)
        this.clientDocuments = response.data
        const clientInfo = this.clients.find(c => c.ID_клиента === clientId)
        this.selectedClientName = clientInfo ? clientInfo.ФИО : 'Клиент'
        this.showClientDocumentsModal = true
      } catch (error) {
        console.error('Ошибка при получении документов клиента:', error)
        alert('Ошибка при получении документов клиента')
      }
    },
    async deleteCar(carId) {
      if (confirm('Вы уверены, что хотите удалить этот автомобиль?')) {
        try {
          await axios.delete(`/api/employee/delete_car/${carId}`)
          alert('Автомобиль успешно удален')
          this.fetchCars() // Обновляем список автомобилей
        } catch (error) {
          console.error('Ошибка при удалении автомобиля:', error)
          alert('Ошибка при удалении автомобиля')
        }
      }
    },
    async deleteService(serviceId) {
      if (confirm('Вы уверены, что хотите удалить эту услугу?')) {
        try {
          await axios.delete(`/api/employee/delete_service/${serviceId}`)
          alert('Услуга успешно удалена')
          this.fetchServices() // Обновляем список услуг
        } catch (error) {
          console.error('Ошибка при удалении услуги:', error)
          alert('Ошибка при удалении услуги')
        }
      }
    },
    async deleteFine(fineId) {
      if (confirm('Вы уверены, что хотите удалить этот тип штрафа?')) {
        try {
          await axios.delete(`/api/employee/delete_fine/${fineId}`)
          alert('Тип штрафа успешно удален')
          this.fetchFines() // Обновляем список типов штрафов
        } catch (error) {
          console.error('Ошибка при удалении типа штрафа:', error)
          alert('Ошибка при удалении типа штрафа')
        }
      }
    },
    async deleteEmployee(employeeId) {
      if (confirm('Вы уверены, что хотите удалить этого сотрудника?')) {
        try {
          await axios.delete(`/api/employee/delete_employee/${employeeId}`)
          alert('Сотрудник успешно удален')
          this.fetchEmployees() // Обновляем список сотрудников
        } catch (error) {
          console.error('Ошибка при удалении сотрудника:', error)
          alert('Ошибка при удалении сотрудника')
        }
      }
    },
    async updateServicePrice(serviceId, newPrice) {
      try {
        await axios.post('/api/employee/update_service_price', {
          ID_услуги: serviceId,
          Стоимость: newPrice
        })
        alert('Стоимость услуги успешно обновлена')
        this.fetchServices() // Обновляем список услуг
      } catch (error) {
        console.error('Ошибка при обновлении стоимости услуги:', error)
        alert('Ошибка при обновлении стоимости услуги')
      }
    },
    async updateEmployeeSalary(employeeId, newSalary) {
      try {
        await axios.post('/api/employee/update_employee_salary', {
          ID_сотрудника: employeeId,
          Оклад: newSalary
        })
        alert('Оклад сотрудника успешно обновлен')
        this.fetchEmployees() // Обновляем список сотрудников
      } catch (error) {
        console.error('Ошибка при обновлении оклада сотрудника:', error)
        alert('Ошибка при обновлении оклада сотрудника')
      }
    },
    async updatePaymentStatus(contractId, newStatus) {
      try {
        await axios.post('/api/employee/update_payment_status', {
          ID_договора: contractId,
          Статус_оплаты: newStatus
        })
        alert('Статус оплаты успешно обновлен')
      } catch (error) {
        console.error('Ошибка при обновлении статуса оплаты:', error)
        alert('Ошибка при обновлении статуса оплаты')
      }
    }
  }
}
</script>

<style scoped>
.employee-cabinet {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 20px;
  background-color: #1a1a1a;
  color: #ffffff;
  min-height: 100vh;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: rgb(66, 185, 131);
  font-size: 2.5rem;
  text-transform: uppercase;
  letter-spacing: 2px;
  position: relative;
}

h1::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background: #0066ff;
  border-radius: 2px;
}

h2 {
  color: rgb(66, 185, 131);
  font-size: 2rem;
  margin-bottom: 20px;
  position: relative;
}

h3 {
  color: rgb(66, 185, 131);
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px 10px 0 0;
  overflow: hidden;
}

.tabs button {
  padding: 12px 24px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  outline: none;
  color: #ffffff;
  transition: all 0.3s ease;
}

.tabs button:hover {
  background: rgba(255, 255, 255, 0.1);
}

.tabs button.active {
  font-weight: bold;
  background: linear-gradient(135deg, #0066ff 0%, #00ff9d 100%);
  color: white;
}

.tab-content {
  margin-top: 20px;
  background: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: 10px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  overflow: hidden;
}

table th, table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

table th {
  background-color: rgba(0, 102, 255, 0.2);
  font-weight: bold;
  color: rgb(66, 185, 131);
}

table tr:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

.add-button {
  background: linear-gradient(135deg, #0066ff 0%, #00ff9d 100%);
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.add-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.modal {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  z-index: 999;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.4);
}

.modal-content {
  background-color: #2a2a2a;
  margin: auto;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  width: 500px;
  max-width: 90%;
  max-height: 85%;
  overflow: auto;
  border-radius: 10px;
  color: #ffffff;
}

.modal-header {
  padding: 10px 16px;
  background-color: rgba(0, 102, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px 10px 0 0;
}

.modal-body {
  padding: 16px;
}

.close {
  color: rgba(255, 255, 255, 0.7);
  float: right;
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
}

.close:hover {
  color: rgb(66, 185, 131);
}

.modal-buttons {
  display: flex;
  gap: 1.5rem;
  margin-top: 2.5rem;
  justify-content: center;
}

.save-button, .cancel-button {
  padding: 12px 30px;
  font-size: 16px;
}

.modal-content h2 {
  color: rgb(66, 185, 131);
  border-bottom: 1px solid rgba(66, 185, 131, 0.3);
  padding-bottom: 15px;
  margin-bottom: 25px;
  font-size: 24px;
  text-align: center;
}

.modal-content label {
  font-size: 16px;
  margin-bottom: 8px;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.2);
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: rgb(66, 185, 131);
}

.form-group input, .form-group select {
  width: 100%;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
  transition: all 0.3s ease;
}

.form-group input:focus, .form-group select:focus {
  outline: none;
  border-color: #0066ff;
  box-shadow: 0 0 0 2px rgba(0, 102, 255, 0.2);
}

.report-selection {
  background: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.report-header {
  margin-bottom: 20px;
}

.report-filters {
  margin-top: 20px;
  padding: 15px;
  background: rgba(0, 102, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(0, 102, 255, 0.1);
}

.report-filters h3 {
  margin-bottom: 15px;
  color: rgb(66, 185, 131);
  border-bottom: 1px solid rgba(66, 185, 131, 0.2);
  padding-bottom: 8px;
}

.filters-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 10px;
}

.filter-item label {
  color: rgb(66, 185, 131);
  margin-bottom: 8px;
  font-weight: 500;
}

.filter-item input,
.filter-item select {
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
  font-size: 14px;
}

.filter-item select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%2300ff9d' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 35px;
  background-color: rgba(42, 42, 42, 0.9) !important;
  font-weight: 500;
  color: #ffffff !important;
}

.filter-item select option {
  background-color: #2a2a2a;
  color: #ffffff;
  padding: 8px;
}

.checkbox-container {
  grid-column: span 2;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: rgba(255, 255, 255, 0.05);
  padding: 10px;
  border-radius: 8px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  margin-bottom: 0;
  cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
  margin-right: 10px;
  width: 16px;
  height: 16px;
}

.generate-button {
  background: linear-gradient(135deg, #0066ff 0%, #00ff9d 100%);
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 25px;
  transition: all 0.3s ease;
  font-weight: bold;
  font-size: 16px;
  display: block;
  width: max-content;
  margin-left: auto;
  margin-right: auto;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

.generate-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.4);
}

.report-types {
  width: 100%;
  margin-top: 10px;
}

.report-types select {
  width: 100%;
  padding: 12px;
  background: rgba(42, 42, 42, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
  font-size: 16px;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%2300ff9d' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 35px;
  font-weight: 500;
}

.report-types select optgroup {
  background: #2a2a2a;
  font-weight: bold;
  color: rgb(66, 185, 131);
  padding: 5px;
}

.report-types select option {
  background: #2a2a2a;
  color: #ffffff;
  padding: 8px;
}

@media (max-width: 768px) {
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .checkbox-container {
    grid-column: span 1;
  }
}

.report-results {
  margin-top: 30px;
  animation: fadeIn 0.5s ease-in-out;
}

.no-data {
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  margin-bottom: 20px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.actions-bar {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
}

.fines-types-section {
  margin-top: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.form-group select {
  width: 100%;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
  transition: all 0.3s ease;
  font-weight: 500;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%2300ff9d' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 30px;
}

.form-group select option {
  background-color: #2a2a2a;
  color: #ffffff;
  padding: 10px;
}

.status-select {
  padding: 5px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  width: 100%;
  cursor: pointer;
}

.status-select option {
  background-color: #1a1a1a;
  color: #ffffff;
}

.edit-input {
  width: 100%;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
}

.date-input {
  width: 100%;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
}

.price-edit-container {
  position: relative;
  display: flex;
  align-items: center;
}

.price-edit-container .currency {
  position: absolute;
  right: 10px;
  color: #ffffff;
  opacity: 0.6;
}

.price-input {
  padding-right: 25px; /* Место для знака валюты */
}

.info-note {
  margin-bottom: 15px;
  font-style: italic;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(66, 185, 131, 0.1);
  padding: 10px;
  border-radius: 8px;
  border-left: 3px solid rgb(66, 185, 131);
}

.info-icon {
  margin-right: 5px;
}

.btn-view {
  background: rgba(0, 102, 255, 0.2);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-view:hover {
  background: rgba(0, 102, 255, 0.4);
}

@media (max-width: 768px) {
  .tabs {
    flex-direction: column;
    border-radius: 10px;
  }
  
  .report-filters {
    grid-template-columns: 1fr;
  }
  
  .tabs button {
    text-align: center;
    padding: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .tabs button:last-child {
    border-bottom: none;
  }
  
  .modal-content {
    width: 95%;
    padding: 20px;
  }
  
  .contact-grid {
    grid-template-columns: 1fr;
  }
}

.clickable-cell {
  cursor: pointer;
  color: #0066ff;
}

/* Дополнительные стили для форм в модальных окнах */
.modal-content .form-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
  padding: 12px;
  width: 100%;
  font-size: 16px;
  margin-bottom: 5px;
}

.form-group {
  margin-bottom: 20px;
}

.modal-content .form-input:focus {
  outline: none;
  border-color: rgb(66, 185, 131);
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.2);
}

.modal-content select.form-input {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%2300ff9d' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 35px;
}

.modal-content select.form-input option {
  background-color: #2a2a2a;
  color: #ffffff;
  padding: 8px;
}

.modal-content input[type="date"].form-input {
  color-scheme: dark;
}

.save-button {
  background: linear-gradient(135deg, #42b983 0%, #3a9f74 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
}

.save-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.cancel-button {
  background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
}

.cancel-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(255, 118, 117, 0.4);
}

/* Специальный стиль только для модального окна "Добавить автомобиль" */
.modal-content.add-car-modal {
 /*  max-height: 80vh;*/
  overflow-y: auto;
  margin-top: 90px; /* Отступ от верха */
  max-height: calc(100vh - 200px); 

}

.delete-button {
  background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
  color: white;
  padding: 5px 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(214, 48, 49, 0.5);
}

.services-section, .employees-section {
  margin-top: 20px;
}

.documents-modal {
  width: 600px;
  max-width: 90%;
}

.documents-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.document-section {
  background: rgba(255, 255, 255, 0.05);
  padding: 15px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.document-section h4 {
  color: rgb(66, 185, 131);
  margin-top: 0;
  margin-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 5px;
}

.document-details p {
  margin: 5px 0;
}

.no-documents {
  text-align: center;
  padding: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
}

/* Специальный стиль только для модального окна "Добавить сотрудника" */
.modal-content.add-employee-modal {
  overflow-y: auto;
  margin-top: 90px; /* Отступ от верха */
  max-height: calc(100vh - 200px); 
}
</style> 