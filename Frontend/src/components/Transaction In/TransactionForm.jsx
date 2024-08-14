import React, { useState } from "react";
import axios from "axios";
import AsyncSelect from "react-select/async";
import { baseUrl } from "../../utils/constants/Constants";
import ProductModal from "./ProductModal";
import Swal from "sweetalert2";

const TransactionForm = () => {
  const [transactionDetails, setTransactionDetails] = useState({
    purchaseDate: "",
    supplierName: "",
    supplierDate: "",
    supplierInvoice: "",
  });

  const [products, setProducts] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [totalQuantity, setTotalQuantity] = useState(0);
  const [remarks, setRemarks] = useState("");

  const handleTransactionDetailChange = (e) => {
    const { name, value } = e.target;
    setTransactionDetails({ ...transactionDetails, [name]: value });
  };

  const addProduct = (product) => {
    setProducts([...products, { ...product, serialNumber: products.length + 1 }]);
    setTotalQuantity(totalQuantity + product.quantity);
  };

  const clearProducts = () => {
    setProducts([]);
    setTotalQuantity(0);
  };

  const saveTransaction = async () => {
    try {
      const response = await axios.post(`${baseUrl}store/transactions/`, {
        ...transactionDetails,
        products,
        remarks,
      });
      Swal.fire("Success", "Transaction saved successfully!", "success");
    } catch (error) {
      console.error("Error saving transaction:", error);
      Swal.fire("Error", "Failed to save the transaction.", "error");
    }
  };

  const handlePrint = () => {
    // Implement print functionality here
    window.print();
  };

  return (
    <div className="container mx-auto p-6">
      <div className="bg-white shadow-md rounded p-6">
        <h2 className="text-2xl font-bold mb-6">Transaction Form</h2>
        
        {/* Transaction Details Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="date"
            name="purchaseDate"
            value={transactionDetails.purchaseDate}
            onChange={handleTransactionDetailChange}
            placeholder="Purchase Date"
            className="border rounded p-2 w-full"
          />
          <input
            type="text"
            name="supplierName"
            value={transactionDetails.supplierName}
            onChange={handleTransactionDetailChange}
            placeholder="Supplier Name"
            className="border rounded p-2 w-full"
          />
          <input
            type="date"
            name="supplierDate"
            value={transactionDetails.supplierDate}
            onChange={handleTransactionDetailChange}
            placeholder="Supplier Date"
            className="border rounded p-2 w-full"
          />
          <input
            type="text"
            name="supplierInvoice"
            value={transactionDetails.supplierInvoice}
            onChange={handleTransactionDetailChange}
            placeholder="Supplier Invoice"
            className="border rounded p-2 w-full"
          />
        </div>

        {/* Add Product Button */}
        <div className="mt-4">
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            onClick={() => setShowModal(true)}
          >
            Add Product
          </button>
        </div>

        {/* Product List Table */}
        <div className="overflow-x-auto mt-4">
          <table className="min-w-full bg-white shadow-md rounded">
            <thead className="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
              <tr>
                <th className="py-3 px-6 text-left">Serial Number</th>
                <th className="py-3 px-6 text-left">Product Code</th>
                <th className="py-3 px-6 text-left">Name</th>
                <th className="py-3 px-6 text-left">Barcode</th>
                <th className="py-3 px-6 text-left">Brand</th>
                <th className="py-3 px-6 text-left">Manufacturing Date</th>
                <th className="py-3 px-6 text-left">Expiry Date</th>
                <th className="py-3 px-6 text-left">Quantity</th>
                <th className="py-3 px-6 text-left">Total</th>
              </tr>
            </thead>
            <tbody className="text-gray-600 text-sm">
              {products.map((product) => (
                <tr key={product.serialNumber}>
                  <td className="py-3 px-6 text-left">{product.serialNumber}</td>
                  <td className="py-3 px-6 text-left">{product.product_code}</td>
                  <td className="py-3 px-6 text-left">{product.name}</td>
                  <td className="py-3 px-6 text-left">{product.barcode}</td>
                  <td className="py-3 px-6 text-left">{product.brand_name}</td>
                  <td className="py-3 px-6 text-left">{product.manufacturing_date}</td>
                  <td className="py-3 px-6 text-left">{product.expiry_date}</td>
                  <td className="py-3 px-6 text-left">{product.quantity}</td>
                  <td className="py-3 px-6 text-left">{product.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Remarks and Total Quantity */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <textarea
            name="remarks"
            value={remarks}
            onChange={(e) => setRemarks(e.target.value)}
            placeholder="Remarks"
            className="border rounded p-2 w-full"
          />
          <div className="text-right">
            <label>Total Quantity: {totalQuantity}</label>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-4 flex justify-between">
          <button
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            onClick={saveTransaction}
          >
            Save Transaction
          </button>
          <button
            className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            onClick={handlePrint}
          >
            Print
          </button>
          <button
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            onClick={clearProducts}
          >
            Clear Products
          </button>
        </div>
      </div>

      {/* Product Modal */}
      {showModal && (
        <ProductModal
          setShowModal={setShowModal}
          addProduct={addProduct}
        />
      )}
    </div>
  );
};

export default TransactionForm;
