import React, { useState, useEffect } from "react";
import axios from "axios";
import AsyncSelect from "react-select/async";
import Swal from "sweetalert2";
import { baseUrl } from "../../utils/constants/Constants";
import ProductModal from "./ProductModal";

const TransactionForm = () => {
  const [transactionDetails, setTransactionDetails] = useState({
    purchaseDate: "",
    supplier: null,
    supplierDate: "",
    supplierInvoice: "",
    products: [],
    remarks: "",
  });

  const [showModal, setShowModal] = useState(false);
  const [totalQuantity, setTotalQuantity] = useState(0);

  useEffect(() => {
    calculateTotalQuantity();
  }, [transactionDetails.products]);

  const handleSupplierChange = (selectedOption) => {
    setTransactionDetails({ ...transactionDetails, supplier: selectedOption });
  };

  const loadSupplierOptions = async (inputValue) => {
    const response = await axios.get(`${baseUrl}store/suppliers/?search=${inputValue}`);
    return response.data.results.map((supplier) => ({
      label: supplier.name,
      value: supplier.id,
    }));
  };

  const handleInputChange = (newValue) => {
    return newValue.replace(/\W/g, '');
  };

  const handleAddProduct = (product) => {
    setTransactionDetails({
      ...transactionDetails,
      products: [...transactionDetails.products, product],
    });
    setShowModal(false);
  };

  const calculateTotalQuantity = () => {
    const total = transactionDetails.products.reduce((sum, product) => sum + product.quantity, 0);
    setTotalQuantity(total);
  };

  const calculateTotal = (product) => {
    const pricePerUnit = product.price || 10; // Replace 10 with the actual price per unit if available
    return product.quantity * pricePerUnit;
  };

  const handleClearProducts = () => {
    setTransactionDetails({ ...transactionDetails, products: [] });
    setTotalQuantity(0);
  };

  const handleSubmit = async () => {
    const transformedData = {
        purchase_date: transactionDetails.purchaseDate,
        supplier: transactionDetails.supplier?.value || null,
        supplier_date: transactionDetails.supplierDate,
        supplier_invoice_number: transactionDetails.supplierInvoice,
        transaction_details: transactionDetails.products.map((product) => ({
            product: product.id, // Ensure this is the product ID (pk)
            manufacturing_date: product.manufacturingDate,
            expiry_date: product.expiryDate,
            quantity: product.quantity,
            total: calculateTotal(product), // Ensure total is included
        })),
        remarks: transactionDetails.remarks,
    };

    try {
        await axios.post(`${baseUrl}store/product-in-transactions/`, transformedData);
        Swal.fire("Success", "Transaction saved successfully", "success");
        handleClearProducts(); // Clear form after submission
    } catch (error) {
        console.error("Error saving transaction:", error);
        Swal.fire("Error", "Failed to save the transaction", "error");
    }
};


  return (
    <div className="container mx-auto p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Purchase Date</label>
          <input
            type="date"
            value={transactionDetails.purchaseDate}
            onChange={(e) => setTransactionDetails({ ...transactionDetails, purchaseDate: e.target.value })}
            placeholder="Select Purchase Date"
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Supplier Name</label>
          <AsyncSelect
            cacheOptions
            loadOptions={loadSupplierOptions}
            onInputChange={handleInputChange}
            onChange={handleSupplierChange}
            isClearable
            placeholder="Search Supplier"
            className="mt-1 block w-full"
            defaultOptions
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Supplier Date</label>
          <input
            type="date"
            value={transactionDetails.supplierDate}
            onChange={(e) => setTransactionDetails({ ...transactionDetails, supplierDate: e.target.value })}
            placeholder="Select Supplier Date"
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Supplier Invoice Number</label>
          <input
            type="text"
            value={transactionDetails.supplierInvoice}
            onChange={(e) => setTransactionDetails({ ...transactionDetails, supplierInvoice: e.target.value })}
            placeholder="Enter Supplier Invoice Number"
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div className="mt-6">
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          onClick={() => setShowModal(true)}
        >
          Add Product
        </button>
      </div>

      <div className="mt-6">
        {transactionDetails.products.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white shadow-md rounded">
              <thead className="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
                <tr>
                  <th className="py-3 px-6 text-left">#</th>
                  <th className="py-3 px-6 text-left">Product Code</th>
                  <th className="py-3 px-6 text-left">Name</th>
                  <th className="py-3 px-6 text-left">Brand</th>
                  <th className="py-3 px-6 text-left">Category</th>
                  <th className="py-3 px-6 text-left">Barcode</th>
                  <th className="py-3 px-6 text-left">Manufacturing Date</th>
                  <th className="py-3 px-6 text-left">Expiry Date</th>
                  <th className="py-3 px-6 text-left">Quantity</th>
                </tr>
              </thead>
              <tbody className="text-gray-600 text-sm">
                {transactionDetails.products.map((product, index) => (
                  <tr key={index} className="border-b border-gray-200 hover:bg-gray-100">
                    <td className="py-3 px-6 text-left">{index + 1}</td>
                    <td className="py-3 px-6 text-left">{product.productCode}</td>
                    <td className="py-3 px-6 text-left">{product.name}</td>
                    <td className="py-3 px-6 text-left">{product.brandName}</td>
                    <td className="py-3 px-6 text-left">{product.categoryName}</td>
                    <td className="py-3 px-6 text-left">{product.barcode}</td>
                    <td className="py-3 px-6 text-left">{product.manufacturingDate}</td>
                    <td className="py-3 px-6 text-left">{product.expiryDate}</td>
                    <td className="py-3 px-6 text-left">{product.quantity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No products added. Click "Add Product" to start.
          </div>
        )}

        {/* Total Quantity */}
        <div className="mt-4 bg-gray-200 p-4 rounded text-right">
          <strong>Total Quantity:</strong> {totalQuantity}
        </div>
      </div>

      <div className="mt-6">
        <label className="block text-sm font-medium text-gray-700">Remarks</label>
        <textarea
          value={transactionDetails.remarks}
          onChange={(e) => setTransactionDetails({ ...transactionDetails, remarks: e.target.value })}
          placeholder="Enter any remarks..."
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div className="mt-6 flex space-x-4">
        <button
          className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          onClick={handleSubmit}
        >
          Save and Print
        </button>
        <button
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          onClick={handleClearProducts}
        >
          Clear
        </button>
      </div>

      {/* Product Modal */}
      {showModal && (
        <ProductModal
          setShowModal={setShowModal}
          addProduct={handleAddProduct}
        />
      )}
    </div>
  );
};

export default TransactionForm;
