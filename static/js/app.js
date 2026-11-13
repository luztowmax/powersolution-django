function getCookie(name){return document.cookie.split(';').map(x=>x.trim()).find(x=>x.startsWith(name+'='))?.split('=').slice(1).join('')||'';}
const tbody=document.getElementById("rows");
const applianceData=window.APPLIANCE_CATALOG;
let lastPayload=null,lastResult=null;

function addRow(defaultId = null) {
    const tr = document.createElement("tr");

    const opts = applianceData.map(a => `
        <option value="${a.id}"
            ${a.id === defaultId ? "selected" : ""}>
            ${a.name}
        </option>
    `).join("");

    tr.innerHTML = `
        <td data-label="Appliance">
            <select class="appselect" aria-label="Appliance">
                ${opts}
            </select>
        </td>

        <td data-label="Quantity">
            <input
                class="qty"
                type="number"
                min="0"
                value="1"
                aria-label="Quantity"
            >
        </td>

        <td data-label="Watts each">
            <input
                class="watts"
                type="number"
                min="0"
                step="1"
                aria-label="Watts each"
            >
        </td>

        <td data-label="Hours/day">
            <input
                class="hours"
                type="number"
                min="0"
                max="24"
                step=".5"
                value="5"
                aria-label="Hours per day"
            >
        </td>

        <td data-label="">
            <button
                type="button"
                class="remove"
                aria-label="Remove appliance"
                title="Remove appliance"
            >
                &times;
            </button>
        </td>
    `;

    tbody.appendChild(tr);

    const sel = tr.querySelector(".appselect");

    const update = () => {
        tr.querySelector(".watts").value =
            applianceData.find(
                a => a.id === Number(sel.value)
            )?.watts || 0;
    };

    sel.addEventListener("change", update);
    update();

    tr.querySelector(".remove").onclick = () => tr.remove();
}

/* =====================================
   INITIALIZE APPLIANCE CALCULATOR
===================================== */

// Connect the Add Appliance button
const addApplianceButton = document.getElementById("add");

if (addApplianceButton) {
    addApplianceButton.addEventListener("click", function () {
        addRow();
    });
}

// Load default appliances when the page opens
if (Array.isArray(applianceData) && applianceData.length > 0) {

    addRow(
        applianceData.find(a => a.name === "LED Light")?.id
    );

    addRow(
        applianceData.find(a => a.name === "Television")?.id
    );

    addRow(
        applianceData.find(a => a.name === "Standing Fan")?.id
    );

} else {
    console.warn("PowerSolution appliance catalogue is empty.");
}

function payload(){
 return {appliances:[...tbody.querySelectorAll("tr")].map(tr=>({appliance_id:Number(tr.querySelector(".appselect").value),quantity:Number(tr.querySelector(".qty").value),watts:Number(tr.querySelector(".watts").value),hours:Number(tr.querySelector(".hours").value)})),
 backup_hours:Number(document.getElementById("backup").value),system_voltage:Number(document.getElementById("voltage").value),
 depth_of_discharge:Number(document.getElementById("dod").value)/100,battery_chemistry:document.getElementById("chemistry").value,power_factor:Number(document.getElementById("pf").value),
 inverter_margin:1+Number(document.getElementById("margin").value)/100,peak_sun_hours:Number(document.getElementById("sun").value),
 pv_derate:Number(document.getElementById("derate").value)/100};
}
const payButton = document.getElementById("pay-full-btn");

document.getElementById("pay-full-btn")
    .addEventListener("click", async function () {
//if (payButton) {
  //  payButton.addEventListener("click", async function () {

        const button = this;
        const quoteId = button.dataset.quoteId;

        if (!quoteId) {
            alert("Please generate a quotation first.");
            return;
        }

        button.disabled = true;
        button.textContent = "Connecting to Paystack...";

        try {
            const response = await fetch(
                `/quote/${quoteId}/pay/`,
                {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    credentials: "same-origin"
                }
            );

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.error || "Payment could not be started."
                );
            }

            window.location.href = result.authorization_url;

        } catch (error) {
            alert(error.message);
            button.disabled = false;
            button.textContent = "Pay Full Amount with Paystack";
        }
    
    });

//function getCookie(name) {
   // const cookie = document.cookie
     //   .split("; ")
       // .find(row => row.startsWith(name + "="));

    //return cookie
      //  ? decodeURIComponent(cookie.split("=")[1])
        //: "";
//}


//payButton.style.display = "inline-block";
//payButton.dataset.quoteId = data.quote_id;
const na=v=>v==null?"Not configured":Number(v).toLocaleString("en-NG");
document.getElementById("calculate").onclick=async()=>{
 const err=document.getElementById("error");err.textContent="";
 try{
  lastPayload=payload();
  const res=await fetch("/api/calculate/",{method:"POST",headers:{"Content-Type":"application/json","X-CSRFToken":getCookie("csrftoken")},body:JSON.stringify(lastPayload)});
  const data=await res.json();if(!res.ok)throw Error(data.error||"Calculation failed.");
  lastResult=data.result;render(lastResult);
 }catch(e){err.textContent=e.message;}
};
function render(r){
 document.getElementById("output").classList.remove("hidden");
 document.getElementById("stats").innerHTML=[
  ["Connected load",`${na(r.total_watts)} W`],["Daily energy",`${r.daily_kwh} kWh`],
  ["Inverter requirement",`${r.required_inverter_kva} kVA`],["PV array",`${na(r.pv_required_w)} W`]
 ].map(x=>`<div class="stat"><small>${x[0]}</small><b>${x[1]}</b></div>`).join("");
 document.getElementById("sizing").innerHTML=[
  ["Inverter recommendation",r.inverter?`${r.inverter.name} (${r.inverter.capacity_kva} kVA)`:"No suitable inverter in catalogue"],
  ["Battery recommendation",r.battery?`${r.battery.quantity} × ${r.battery.spec} (${r.battery.series} series × ${r.battery.parallel} parallel)`:"No compatible battery in catalogue"],
  ["Backup target",`${r.backup_hours} hours`],["Solar panel recommendation",r.solar_panel?`${r.solar_panel.quantity} × ${r.solar_panel.wattage}W panels`:"No solar panel in catalogue"],
  ["Required PV capacity",`${na(r.pv_required_w)} W`],["Energy per day",`${r.daily_kwh} kWh`]
 ].map(x=>`<div class="sizingrow"><span>${x[0]}</span><b>${x[1]}</b></div>`).join("");
 document.getElementById("items").innerHTML=r.items.map(x=>`<tr><td>${x.name}</td><td>${x.quantity}</td><td>₦${na(x.unit_price)}</td><td>₦${na(x.line_total)}</td></tr>`).join("");
 document.getElementById("total").textContent=`Estimated total: ₦${na(r.estimated_total)}`;
 document.getElementById("breakdown").innerHTML=r.breakdown.map(x=>`<tr><td>${x.name}</td><td>${x.quantity}</td><td>${na(x.total_watts)}</td><td>${x.hours}</td><td>${na(x.daily_wh)}</td></tr>`).join("");
 document.getElementById("warnings").innerHTML=r.warnings.map(x=>`<li>${x}</li>`).join("");
 document.getElementById("output").scrollIntoView({behavior:"smooth"});
}

document.getElementById("makeQuote").onclick = async () => {
    const msg = document.getElementById("quoteMessage");
    msg.textContent = "";

    if (!lastPayload) {
        msg.textContent = "Calculate the system first.";
        return;
    }

    const customer = {
        name: document.getElementById("custName").value,
        email: document.getElementById("custEmail").value,
        phone: document.getElementById("custPhone").value,
        address: document.getElementById("custAddress").value
    };

    try {
        const res = await fetch("/api/quote/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                ...lastPayload,
                customer
            })
        });

        const data = await res.json();

        if (!res.ok || !data.success) {
            throw new Error(
                data.error || "Could not save quotation."
            );
        }

        // Display quotation download link
        msg.innerHTML = `Quotation saved. <a href="${data.pdf_url}" target="_blank">Download your PDF quotation</a>`;

        // Enable Paystack only after a quote is saved
        if (payButton) {
            payButton.dataset.quoteId = data.quote_id;
            payButton.style.display = "inline-block";
            payButton.hidden = false;
        }

    } catch (e) {
        msg.textContent = e.message;
    }
};

