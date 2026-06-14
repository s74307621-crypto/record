jQuery(document).ready(function($) {
    'use strict';
    
    var currentRecordId = null;
    var currentCustomerId = null;
    
    // Initialize Select2 for patient selection
    function initPatientSelect2() {
        $('.mr-patient-select2').select2({
            ajax: {
                url: mrAdminAjax.ajax_url,
                dataType: 'json',
                delay: 250,
                data: function(params) {
                    return {
                        action: 'mr_search_patients',
                        term: params.term,
                        nonce: mrAdminAjax.nonce
                    };
                },
                processResults: function(data) {
                    return {
                        results: data.results
                    };
                }
            },
            placeholder: 'جستجو و انتخاب بیمار...',
            minimumInputLength: 1,
            language: {
                searching: function() {
                    return 'در حال جستجو...';
                },
                noResults: function() {
                    return 'بیماری یافت نشد';
                }
            }
        });
    }
    
    // Show create record form - Simplified to just show confirmation modal
    $(document).on('click', '.mr-create-record-btn', function() {
        var patientId = $(this).closest('tr').data('patient-id');
        var patientName = $(this).closest('tr').find('td:nth-child(2)').text();
        
        if (confirm('آیا مطمئن هستید که می‌خواهید برای بیمار "' + patientName + '" پرونده ایجاد کنید؟')) {
            // Auto-create record with minimal data
            $.ajax({
                url: mrAdminAjax.ajax_url,
                type: 'POST',
                data: {
                    action: 'mr_create_medical_record',
                    nonce: mrAdminAjax.nonce,
                    customer_id: patientId,
                    doctor_id: 1, // Default to first doctor, can be changed later
                    blood_group: '',
                    age: 0,
                    special_diseases: '',
                    current_medications: ''
                },
                success: function(response) {
                    if (response.success) {
                        showToast(response.data.message, 'success');
                        setTimeout(function() {
                            location.reload();
                        }, 1500);
                    } else {
                        showToast(response.data.message || 'خطایی رخ داده است', 'error');
                    }
                },
                error: function() {
                    showToast('خطای سرور', 'error');
                }
            });
        }
    });
    
    // Initialize create record
    $(document).on('click', '#mr-init-create-record', function() {
        var patientId = $('.mr-patient-select2').val();
        var patientText = $('.mr-patient-select2').select2('data')[0]?.text;
        
        if (!patientId) {
            alert('لطفا یک بیمار انتخاب کنید');
            return;
        }
        
        currentCustomerId = patientId;
        
        $('#mr-selected-patient-info').html('<strong>بیمار انتخاب شده:</strong> ' + patientText);
        $('#mr-full-create-form').slideDown();
        $('#mr-create-record-form').slideUp();
    });
    
    // Cancel create record
    $(document).on('click', '#mr-cancel-create-record', function() {
        $('#mr-full-create-form').slideUp(function() {
            $('#mr-create-record-form').slideDown();
            $('#mr-create-record-form .mr-patient-select2').val(null).trigger('change');
        });
        currentCustomerId = null;
    });
    
    // Submit create record
    $(document).on('click', '#mr-submit-create-record', function() {
        var doctorId = $('[name="doctor_id"]').val();
        var bloodGroup = $('[name="blood_group"]').val();
        var age = $('[name="age"]').val();
        var specialDiseases = $('[name="special_diseases"]').val();
        var currentMedications = $('[name="current_medications"]').val();
        
        if (!doctorId) {
            showToast('لطفا پزشک را انتخاب کنید', 'error');
            return;
        }
        
        $.ajax({
            url: mrAdminAjax.ajax_url,
            type: 'POST',
            data: {
                action: 'mr_create_medical_record',
                nonce: mrAdminAjax.nonce,
                customer_id: currentCustomerId,
                doctor_id: doctorId,
                blood_group: bloodGroup,
                age: age,
                special_diseases: specialDiseases,
                current_medications: currentMedications
            },
            success: function(response) {
                if (response.success) {
                    showToast(response.data.message, 'success');
                    setTimeout(function() {
                        location.reload();
                    }, 1500);
                } else {
                    showToast(response.data.message || 'خطایی رخ داده است', 'error');
                }
            },
            error: function() {
                showToast('خطای سرور', 'error');
            }
        });
    });
    
    // View record
    $(document).on('click', '.mr-view-record', function() {
        var recordId = $(this).data('record-id');
        currentRecordId = recordId;
        
        $('#mr-view-record-container').slideDown();
        loadRecordDetails(recordId);
        $('html, body').animate({
            scrollTop: $('#mr-view-record-container').offset().top - 100
        }, 500);
    });
    
    // Load record details
    function loadRecordDetails(recordId) {
        $.ajax({
            url: mrAdminAjax.ajax_url,
            type: 'GET',
            data: {
                action: 'mr_get_medical_record',
                nonce: mrAdminAjax.nonce,
                record_id: recordId
            },
            success: function(response) {
                if (response.success) {
                    var record = response.data.record;
                    var html = '<h3>جزئیات پرونده</h3>';
                    html += '<p><strong>شناسه:</strong> ' + record.id + '</p>';
                    html += '<p><strong>گروه خونی:</strong> ' + (record.blood_group || '-') + '</p>';
                    html += '<p><strong>سن:</strong> ' + (record.age || '-') + '</p>';
                    html += '<p><strong>بیماری‌های خاص:</strong> ' + (record.special_diseases || '-') + '</p>';
                    html += '<p><strong>داروهای مصرفی:</strong> ' + (record.current_medications || '-') + '</p>';
                    html += '<p><strong>تاریخ ایجاد:</strong> ' + record.created_at + '</p>';
                    
                    $('#mr-view-record-container').html(html);
                }
            }
        });
    }
    
    // Delete record
    $(document).on('click', '.mr-delete-record', function() {
        if (!confirm(mrAdminAjax.strings.confirm_delete)) {
            return;
        }
        
        var recordId = $(this).data('record-id');
        var $row = $(this).closest('tr');
        
        $.ajax({
            url: mrAdminAjax.ajax_url,
            type: 'POST',
            data: {
                action: 'mr_delete_medical_record',
                nonce: mrAdminAjax.nonce,
                record_id: recordId
            },
            success: function(response) {
                if (response.success) {
                    showToast(response.data.message, 'success');
                    $row.fadeOut();
                } else {
                    showToast(response.data.message || 'خطایی رخ داده است', 'error');
                }
            },
            error: function() {
                showToast('خطای سرور', 'error');
            }
        });
    });
    
    // Toast notification
    function showToast(message, type) {
        var $toast = $('<div class="mr-toast">' + message + '</div>');
        $toast.addClass(type);
        $('body').append($toast);
        
        setTimeout(function() {
            $toast.addClass('show');
        }, 100);
        
        setTimeout(function() {
            $toast.removeClass('show');
            setTimeout(function() {
                $toast.remove();
            }, 500);
        }, 3000);
    }
});
