import React, { useState, useEffect } from "react";
import axios from "axios";
import { baseUrl } from "../../utils/constants/Constants";
import Swal from "sweetalert2";

const InventoryList = () => {
  const [inventory, setInventory] = useState([]);
  const [showExpired, setShowExpired] = useState(false);

  useEffect(() => {
    fetchInventory();
  }, [showExpired]);

  const fetchInventory = async () => {
    try {
      const response = await axios.get(
        `${baseUrl}store/inventory/?expired=${showExpired}`
      );
      setInventory(response.data.results);
    } catch (error) {
      console.error("Error fetching inventory:", error);
      Swal.fire("Error", "Failed to fetch inventory data", "error");
    }
  };

  const handleShowExpired = () => {
    setShowExpired((prev) => !prev);
  };

  const getRowClassName = (remaining_quantity) => {
    if (remaining_quantity === 0) {
      return "bg-red-500 text-white";
    } else if (remaining_quantity < 10) {
      return "bg-yellow-500 text-white";
    }
    return "";
  };

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center py-4">
        <h2 className="text-2xl font-bold">Inventory</h2>
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          onClick={handleShowExpired}
        >
          {showExpired ? "Show All Products" : "Show Expired Products"}
        </button>
      </div>

      {inventory.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white shadow-md rounded">
            <thead className="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
              <tr>
                <th className="py-3 px-6 text-left">#</th>
                <th className="py-3 px-6 text-left">Product Code</th>
                <th className="py-3 px-6 text-left">Name</th>
                <th className="py-3 px-6 text-left">Barcode</th>
                <th className="py-3 px-6 text-left">Category</th>
                <th className="py-3 px-6 text-left">Brand</th>
                <th className="py-3 px-6 text-left">Supplier</th>
                <th className="py-3 px-6 text-left">Purchase Date</th>
                <th className="py-3 px-6 text-left">Manufacturing Date</th>
                <th className="py-3 px-6 text-left">Expiry Date</th>
                <th className="py-3 px-6 text-left">Purchased Quantity</th> {/* New field */}
                <th className="py-3 px-6 text-left">Remaining Quantity</th> {/* New field */}
              </tr>
            </thead>
            <tbody className="text-gray-600 text-sm">
              {inventory.map((item, index) => (
                <tr
                  key={index}
                  className={`border-b border-gray-200 hover:bg-gray-100 ${getRowClassName(
                    item.remaining_quantity
                  )}`}
                >
                  <td className="py-3 px-6 text-left">{index + 1}</td>
                  <td className="py-3 px-6 text-left">{item.product_code}</td>
                  <td className="py-3 px-6 text-left">{item.name}</td>
                  <td className="py-3 px-6 text-left">{item.barcode}</td>
                  <td className="py-3 px-6 text-left">{item.category_name}</td>
                  <td className="py-3 px-6 text-left">{item.brand_name}</td>
                  <td className="py-3 px-6 text-left">{item.supplier_name}</td>
                  <td className="py-3 px-6 text-left">{item.purchase_date}</td>
                  <td className="py-3 px-6 text-left">{item.manufacturing_date}</td>
                  <td className="py-3 px-6 text-left">{item.expiry_date}</td>
                  <td className="py-3 px-6 text-left">{item.purchased_quantity}</td> {/* Displaying Purchased Quantity */}
                  <td className="py-3 px-6 text-left">{item.remaining_quantity}</td> {/* Displaying Remaining Quantity */}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          No products found. {showExpired ? "No expired products available." : "Inventory is empty."}
        </div>
      )}
    </div>
  );
};

export default InventoryList;
