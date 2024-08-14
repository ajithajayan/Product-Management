import React, { useState } from "react";
import axios from "axios";
import AsyncSelect from "react-select/async";
import { baseUrl } from "../../utils/constants/Constants";

const ProductModal = ({ setShowModal, addProduct }) => {
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [productDetails, setProductDetails] = useState({
    manufacturing_date: "",
    expiry_date: "",
    quantity: 0,
    total: 0,
  });

  const loadProductOptions = async (inputValue) => {
    const response = await axios.get(
      `${baseUrl}store/products/search_codes/?query=${inputValue}`
    );
    return response.data.map((product) => ({
      label: product.name + " (" + product.product_code + ")",
      value: product,
    }));
  };

  const handleProductChange = (selectedOption) => {
    setSelectedProduct(selectedOption.value);
  };

  const handleDetailChange = (e) => {
    const { name, value } = e.target;
    setProductDetails({ ...productDetails, [name]: value });
  };

  const handleSaveProduct = () => {
    addProduct({
      ...selectedProduct,
      ...productDetails,
    });
    setShowModal(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white w-full max-w-3xl mx-4 shadow-lg rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-6">Add Product to Transaction</h2>

        <AsyncSelect
          loadOptions={loadProductOptions}
          onChange={handleProductChange}
          isClearable
          placeholder="Search by Product ID or Name"
          className="mb-4"
        />

        {selectedProduct && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Product Code</label>
              <input
                type="text"
                value={selectedProduct.product_code}
                readOnly
                className="border rounded p-2 w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Barcode</label>
              <input
                type="text"
                value={selectedProduct.barcode}
                readOnly
                className="border rounded p-2 w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Brand</label>
              <input
                type="text"
                value={selectedProduct.brand_name}
                readOnly
                className="border rounded p-2 w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Manufacturing Date</label>
              <input
                type="date"
                name="manufacturing_date"
                value={productDetails.manufacturing_date}
                onChange={handleDetailChange}
                className="border rounded p-2 w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Expiry Date</label>
              <input
                type="date"
                name="expiry_date"
                value={productDetails.expiry_date}
                onChange={handleDetailChange}
                className="border rounded p-2 w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Quantity</label>
              <input
                type="number"
                name="quantity"
                value={productDetails.quantity}
                onChange={handleDetailChange}
                className="border rounded p-2 w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Total</label>
              <input
                type="number"
                name="total"
                value={productDetails.total}
                onChange={handleDetailChange}
                className="border rounded p-2 w-full"
              />
            </div>
          </div>
        )}

        <div className="mt-4 flex justify-end space-x-2">
          <button
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            onClick={handleSaveProduct}
          >
            Save Product
          </button>
          <button
            className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            onClick={() => setShowModal(false)}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductModal;
