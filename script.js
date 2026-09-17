class Car {
  constructor(plate, vehicleType) {
    this.plate = plate;
    this.vehicleType = vehicleType.toLowerCase();
    this.isEv = this.vehicleType === 'ev';
  }
}

class ParkingGarage {
  constructor(spots = { compact: 1, standard: 2, ev: 1 }, rates = { first_hour: 10, additional_hour: 6, daily_cap: 40 }) {
    this.spots = { compact: 0, standard: 0, ev: 0, ...spots };
    this.rates = { first_hour: 10, additional_hour: 6, daily_cap: 40, ...rates };
    this.activeCars = new Map();
    this.occupancy = { compact: 0, standard: 0, ev: 0 };
    this.log = [];
  }

  availableSpots() {
    return {
      compact: Math.max(0, this.spots.compact - this.occupancy.compact),
      standard: Math.max(0, this.spots.standard - this.occupancy.standard),
      ev: Math.max(0, this.spots.ev - this.occupancy.ev),
    };
  }

  isSpotFree(type) {
    const key = String(type).toLowerCase();
    return this.availableSpots()[key] > 0;
  }

  checkIn(car, checkInTime = new Date()) {
    const plate = String(car.plate || '').trim();
    const type = String(car.vehicleType || '').toLowerCase();

    if (!plate) throw new Error('Plate is required');
    if (!['compact', 'standard', 'ev'].includes(type)) throw new Error('Unsupported vehicle type');
    if (this.activeCars.has(plate)) throw new Error(`Car ${plate} is already parked`);

    const spotType = this.resolveSpotType(type);
    this.occupancy[spotType] += 1;

    const record = {
      plate,
      vehicleType: type,
      spotType,
      checkInTime: new Date(checkInTime),
    };

    this.activeCars.set(plate, record);
    this.log.push(`Checked in ${plate} in ${spotType} spot`);
    return record;
  }

  resolveSpotType(type) {
    if (type === 'ev') {
      if (!this.spots.ev || this.occupancy.ev >= this.spots.ev) {
        throw new Error('No EV spots available');
      }
      return 'ev';
    }

    if (type === 'compact') {
      if (!this.spots.compact || this.occupancy.compact >= this.spots.compact) {
        throw new Error('No compact spots available');
      }
      return 'compact';
    }

    if (!this.spots.standard || this.occupancy.standard >= this.spots.standard) {
      throw new Error('No standard spots available');
    }
    return 'standard';
  }

  checkOut(plate, checkOutTime = new Date()) {
    const record = this.activeCars.get(String(plate));
    if (!record) throw new Error(`Car ${plate} not found`);

    const outTime = new Date(checkOutTime);
    const durationSeconds = Math.max(0, (outTime - new Date(record.checkInTime)) / 1000);
    const fee = this.calculateFee(durationSeconds);

    this.activeCars.delete(String(plate));
    this.occupancy[record.spotType] = Math.max(0, this.occupancy[record.spotType] - 1);
    this.log.push(`Checked out ${plate} for $${fee}`);

    return fee;
  }

  calculateFee(durationSeconds) {
    const totalHours = Math.max(1, Math.ceil(durationSeconds / 3600));
    const firstHour = Number(this.rates.first_hour || 0);
    const additionalHour = Number(this.rates.additional_hour || 0);
    const dailyCap = Number(this.rates.daily_cap || 0);

    let fee = totalHours <= 1
      ? firstHour
      : firstHour + (totalHours - 1) * additionalHour;

    if (dailyCap && fee > dailyCap) fee = dailyCap;
    return fee;
  }
}

const state = {
  garage: new ParkingGarage(),
};

const els = {
  compactSpots: document.getElementById('compact-spots'),
  standardSpots: document.getElementById('standard-spots'),
  evSpots: document.getElementById('ev-spots'),
  firstHour: document.getElementById('first-hour'),
  additionalHour: document.getElementById('additional-hour'),
  dailyCap: document.getElementById('daily-cap'),
  availability: document.getElementById('availability'),
  carsBody: document.getElementById('cars-body'),
  log: document.getElementById('log'),
  checkinForm: document.getElementById('checkin-form'),
  checkoutForm: document.getElementById('checkout-form'),
};

function formatDateTime(value) {
  if (!value) return '—';
  const date = new Date(value);
  return date.toLocaleString();
}

function setStatus(message, type = 'success') {
  const existing = document.querySelector('.status-message');
  if (existing) existing.remove();

  const node = document.createElement('div');
  node.className = `status-message ${type}`;
  node.textContent = message;
  document.body.appendChild(node);
}

function renderAvailability() {
  const available = state.garage.availableSpots();
  const types = ['compact', 'standard', 'ev'];

  els.availability.innerHTML = types.map((type) => `
    <div class="availability-item">
      <span>${type.toUpperCase()}</span>
      <strong>${available[type]}</strong>
    </div>
  `).join('');
}

function renderCars() {
  const rows = [...state.garage.activeCars.values()];

  if (!rows.length) {
    els.carsBody.innerHTML = `<tr><td colspan="4">No cars parked</td></tr>`;
    return;
  }

  els.carsBody.innerHTML = rows.map((car) => `
    <tr>
      <td>${car.plate}</td>
      <td>${car.vehicleType}</td>
      <td>${car.spotType}</td>
      <td>${formatDateTime(car.checkInTime)}</td>
    </tr>
  `).join('');
}

function renderLog() {
  const entries = state.garage.log.slice(-10).reverse();
  els.log.innerHTML = entries.map((entry) => `<li>${entry}</li>`).join('');
}

function renderAll() {
  renderAvailability();
  renderCars();
  renderLog();
}

document.getElementById('apply-setup').addEventListener('click', () => {
  state.garage = new ParkingGarage(
    {
      compact: Number(els.compactSpots.value || 0),
      standard: Number(els.standardSpots.value || 0),
      ev: Number(els.evSpots.value || 0),
    },
    {
      first_hour: Number(els.firstHour.value || 0),
      additional_hour: Number(els.additionalHour.value || 0),
      daily_cap: Number(els.dailyCap.value || 0),
    }
  );
  setStatus('Garage setup updated', 'success');
  renderAll();
});

els.checkinForm.addEventListener('submit', (event) => {
  event.preventDefault();
  try {
    const plate = document.getElementById('plate-in').value.trim();
    const vehicleType = document.getElementById('type-in').value;
    const checkInTime = document.getElementById('checkin-time').value ? new Date(document.getElementById('checkin-time').value) : new Date();

    state.garage.checkIn(new Car(plate, vehicleType), checkInTime);
    setStatus(`Checked in ${plate}`, 'success');
    els.checkinForm.reset();
    renderAll();
  } catch (error) {
    setStatus(error.message, 'error');
  }
});

els.checkoutForm.addEventListener('submit', (event) => {
  event.preventDefault();
  try {
    const plate = document.getElementById('plate-out').value.trim();
    const checkOutTime = document.getElementById('checkout-time').value ? new Date(document.getElementById('checkout-time').value) : new Date();

    const fee = state.garage.checkOut(plate, checkOutTime);
    setStatus(`Checked out ${plate}. Fee: $${fee}`, 'success');
    els.checkoutForm.reset();
    renderAll();
  } catch (error) {
    setStatus(error.message, 'error');
  }
});

function seedDemo() {
  state.garage = new ParkingGarage({ compact: 1, standard: 2, ev: 1 }, { first_hour: 10, additional_hour: 6, daily_cap: 40 });
  const now = new Date();
  const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
  state.garage.checkIn(new Car('ABC-123', 'standard'), oneHourAgo);
  state.garage.checkIn(new Car('EV-1', 'ev'), new Date(now.getTime() - 2 * 60 * 60 * 1000));
  renderAll();
}

seedDemo();
