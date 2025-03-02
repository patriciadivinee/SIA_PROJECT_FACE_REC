$("#my-form").validate({
    rules: {
        firstname: "required",
        lastname: "required",
        address: "required",
        gender: "required",
        email:"required",

        mobile: {
            required: true,
            number: true,
            minlength: 11,
            maxlength: 11,
            mobilePh: true

        },

        newpass: {
            required: true,
            minlength: 8
        },

        confirmpass: {
            minlength:8,
            equalTo: "#newPassword"
        },
        emailaddress: {
            email: true
        },
        image: {
            accept: "image/*",
            maxFileSize: undefined
        }
    },

    messages: {
        firstname: "Enter Firstname",
        lastname: "Enter Lastname",
        address: "Enter Address",
        gender: "Gender is required",
        mobile: {
            required: "Mobile number is required",
            minlength: "Mobile number must be 11 digits",
            maxlength: "Mobile number must be 11 digits",
            number: "Please enter a valid number",
        },
        emailaddress: "e.g. example@gmail.com",
        image: {
            extension: "Only jpg, jpeg, or png files are allowed",
            maxFileSize: "The file size must be less than {0} KB"
        },
        newpass:{
            required: 'Password is required',
            minlength: 'Atleast 8 characters '
        },
        confirmpass: {
            required: "Password is required",
            minlength: "Atleast 8 characters",
            equalTo: "Passwords do not match"
        },

    },

    errorPlacement: function (error, element) {
        if (element.attr("name") === "gender") {
            error.insertAfter("#gender-label");
        } else if (element.attr("name") === "newpass" || element.attr("name") === "confirmpass") {
            // Display password error message at the bottom of the password input
            error.insertAfter(element.parent().parent()); // Assuming two levels up in the DOM structure
        } else {
            error.insertAfter(element);
        }
    },

    submitHandler: function (form) {
        form.submit();
    }
});
jQuery.validator.addMethod("mobilePh", function (phone_number, element) {
    phone_number = phone_number.replace(/\s+/g, "");
    return this.optional(element) || phone_number.length == 11 &&
        phone_number.match(/^(\+?63|0)9\d{9}$/);
}, "Please enter a valid Philippines mobile number.");