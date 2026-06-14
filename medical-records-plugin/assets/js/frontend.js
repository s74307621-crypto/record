jQuery(document).ready(function($) {
    'use strict';
    
    var currentRecordId = null;
    var currentCustomerId = null;
    var uploadedFiles = [];
    
    // Initialize Select2 for patient selection (Doctor view)
    function initPatientSelect2() {
        if ($('.mr-patient-select2').length === 0) return;
        
        $('.mr-patient-select2').select2({
            ajax: {
                url: mrFrontendAjax.ajax_url,
                dataType: 'json',
                delay: 250,
                data: function(params) {
                    return {
                        action: 'mr_search_patients',
                        term: params.term,
                        nonce: mrFrontendAjax.nonce
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
    
    // Show create form button
    $(document).on('click', '#mr-show-create-form', function() {
        $('#mr-create-form-wrapper').slideToggle();
        initPatientSelect2();
    });
    
    // Initialize create record
    $(document).on('click', '#mr-init-create-record', function() {
        var patientId = $('.mr-patient-select2').val();
        var patientText = $('.mr-patient-select2').select2('data')[0]?.text;
        
        if (!patientId) {
            showToast('لطفا یک بیمار انتخاب کنید', 'error');
            return;
        }
        
        currentCustomerId = patientId;
        
        $('.mr-selected-patient-info').html('<strong>بیمار انتخاب شده:</strong> ' + patientText);
        $('#mr-full-create-form').slideDown();
    });
    
    // Cancel create record
    $(document).on('click', '#mr-cancel-create-record', function() {
        $('#mr-full-create-form').slideUp(function() {
            $('#mr-create-form-wrapper .mr-patient-select2').val(null).trigger('change');
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
            url: mrFrontendAjax.ajax_url,
            type: 'POST',
            data: {
                action: 'mr_create_medical_record',
                nonce: mrFrontendAjax.nonce,
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
    
    // Back to list
    $(document).on('click', '.mr-back-to-list', function() {
        $('#mr-view-record-section').slideUp();
        $('#mr-create-record-section').slideDown();
        currentRecordId = null;
    });
    
    // Load visits
    function loadVisits(recordId, filters) {
        if (!recordId) return;
        
        $.ajax({
            url: mrFrontendAjax.ajax_url,
            type: 'GET',
            data: $.extend({
                action: 'mr_get_visits',
                nonce: mrFrontendAjax.nonce,
                medical_record_id: recordId
            }, filters),
            success: function(response) {
                if (response.success) {
                    renderVisits(response.data.visits);
                }
            }
        });
    }
    
    // Render visits table
    function renderVisits(visits) {
        var html = '';
        if (visits.length === 0) {
            html = '<tr><td colspan="4">ویزیتی یافت نشد</td></tr>';
        } else {
            $.each(visits, function(i, visit) {
                var visitDate = new Date(visit.visit_date);
                var persianDate = toPersianDate(visitDate);
                
                html += '<tr>';
                html += '<td>' + persianDate + '</td>';
                html += '<td>' + (visit.doctor_name || '-') + '</td>';
                html += '<td>' + (visit.clinic_name || '-') + '</td>';
                html += '<td><button class="button button-small mr-view-visit" data-visit-id="' + visit.id + '">مشاهده کامل</button></td>';
                html += '</tr>';
            });
        }
        $('#mr-visits-tbody').html(html);
    }
    
    // View visit details
    $(document).on('click', '.mr-view-visit', function() {
        var visitId = $(this).data('visit-id');
        
        $.ajax({
            url: mrFrontendAjax.ajax_url,
            type: 'GET',
            data: {
                action: 'mr_get_visit_details',
                nonce: mrFrontendAjax.nonce,
                visit_id: visitId
            },
            success: function(response) {
                if (response.success) {
                    showVisitDetailsModal(response.data.visit);
                }
            }
        });
    });
    
    // Show visit details modal
    function showVisitDetailsModal(visit) {
        var html = '';
        html += '<p><strong>پزشک:</strong> ' + (visit.doctor_name || '-') + '</p>';
        html += '<p><strong>کلینیک:</strong> ' + (visit.clinic_name || '-') + '</p>';
        html += '<p><strong>تاریخ:</strong> ' + toPersianDate(new Date(visit.visit_date)) + '</p>';
        html += '<hr>';
        html += '<p><strong>علت مراجعه:</strong></p><p>' + (visit.complaint || '-') + '</p>';
        html += '<p><strong>تشخیص:</strong></p><p>' + (visit.diagnosis || '-') + '</p>';
        html += '<p><strong>داروها:</strong></p><p>' + (visit.medications || '-') + '</p>';
        html += '<p><strong>فایل‌ها:</strong></p>';
        
        if (visit.files) {
            try {
                var files = JSON.parse(visit.files);
                $.each(files, function(i, file) {
                    html += '<div style="margin: 5px 0;"><a href="' + file.url + '" target="_blank" class="mr-file-link">' + file.title + '</a></div>';
                });
            } catch(e) {
                html += '<p>' + visit.files + '</p>';
            }
        } else {
            html += '<p>-</p>';
        }
        
        $('#mr-visit-details-content').html(html);
        $('#mr-visit-details-modal').fadeIn();
    }
    
    // Close modal
    $(document).on('click', '.mr-close-modal', function() {
        $(this).closest('.mr-modal').fadeOut();
    });
    
    // Show visit form
    $(document).on('click', '#mr-show-visit-form', function() {
        $('#mr-visit-form-wrapper').slideToggle();
    });
    
    // Cancel visit form
    $(document).on('click', '#mr-cancel-visit', function() {
        $('#mr-visit-form-wrapper').slideUp();
    });
    
    // Add medication row
    $(document).on('click', '#mr-add-medication', function() {
        var row = '<div class="mr-medication-row">';
        row += '<input type="text" name="medication_name[]" placeholder="نام دارو" class="regular-text">';
        row += '<input type="text" name="medication_usage[]" placeholder="نحوه مصرف" class="regular-text">';
        row += '<button class="button mr-remove-medication">×</button>';
        row += '</div>';
        $('#mr-medications-container').append(row);
    });
    
    // Remove medication row
    $(document).on('click', '.mr-remove-medication', function() {
        $(this).closest('.mr-medication-row').remove();
    });
    
    // Add file row
    $(document).on('click', '#mr-add-file', function() {
        var row = '<div class="mr-file-row">';
        row += '<input type="text" name="file_title[]" placeholder="عنوان فایل" class="regular-text">';
        row += '<input type="file" name="file_upload[]" class="mr-file-upload">';
        row += '<button class="button mr-remove-file">×</button>';
        row += '</div>';
        $('#mr-files-container').append(row);
    });
    
    // Remove file row
    $(document).on('click', '.mr-remove-file', function() {
        $(this).closest('.mr-file-row').remove();
    });
    
    // Upload file
    function uploadFile(fileInput) {
        var file = fileInput.files[0];
        if (!file) return Promise.reject('فایلی انتخاب نشده');
        
        var formData = new FormData();
        formData.append('file', file);
        formData.append('action', 'mr_upload_file');
        
        return $.ajax({
            url: mrFrontendAjax.ajax_url,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false
        });
    }
    
    // Submit visit
    $(document).on('click', '#mr-submit-visit', function() {
        var complaint = $('[name="complaint"]').val();
        var diagnosis = $('[name="diagnosis"]').val();
        
        if (!complaint || !diagnosis) {
            showToast('لطفا علت مراجعه و تشخیص را وارد کنید', 'error');
            return;
        }
        
        // Collect medications
        var medications = [];
        $('.mr-medication-row').each(function() {
            var name = $(this).find('[name="medication_name[]"]').val();
            var usage = $(this).find('[name="medication_usage[]"]').val();
            if (name) {
                medications.push({name: name, usage: usage});
            }
        });
        
        // Upload files and collect
        var fileUploads = $('.mr-file-row');
        var uploadPromises = [];
        
        fileUploads.each(function() {
            var fileInput = $(this).find('.mr-file-upload')[0];
            var title = $(this).find('[name="file_title[]"]').val();
            
            if (fileInput.files.length > 0) {
                uploadPromises.push(uploadFile(fileInput).then(function(response) {
                    if (response.success) {
                        return {title: title || response.data.file_name, url: response.data.file_url};
                    }
                    return null;
                }));
            }
        });
        
        Promise.all(uploadPromises).then(function(uploadedFiles) {
            var filesData = uploadedFiles.filter(function(f) { return f !== null; });
            
            $.ajax({
                url: mrFrontendAjax.ajax_url,
                type: 'POST',
                data: {
                    action: 'mr_create_visit',
                    nonce: mrFrontendAjax.nonce,
                    medical_record_id: currentRecordId,
                    doctor_id: get_current_user_id(),
                    clinic_id: 1,
                    complaint: complaint,
                    diagnosis: diagnosis,
                    medications: JSON.stringify(medications),
                    files: JSON.stringify(filesData)
                },
                success: function(response) {
                    if (response.success) {
                        showToast(response.data.message, 'success');
                        $('#mr-visit-form-wrapper').slideUp();
                        loadVisits(currentRecordId, {});
                    } else {
                        showToast(response.data.message || 'خطایی رخ داده است', 'error');
                    }
                },
                error: function() {
                    showToast('خطای سرور', 'error');
                }
            });
        }).catch(function(err) {
            showToast('خطا در آپلود فایل', 'error');
        });
    });
    
    // Apply filters
    $(document).on('click', '#mr-apply-filters', function() {
        var filters = {};
        var clinicId = $('#mr-filter-clinic').val();
        var doctorId = $('#mr-filter-doctor').val();
        var dateFrom = $('#mr-filter-date-from').val();
        var dateTo = $('#mr-filter-date-to').val();
        
        if (clinicId) filters.clinic_id = clinicId;
        if (doctorId) filters.doctor_id = doctorId;
        if (dateFrom) filters.date_from = dateFrom;
        if (dateTo) filters.date_to = dateTo;
        
        loadVisits(currentRecordId, filters);
    });
    
    // Patient view - Show edit history
    $(document).on('click', '#mr-show-edit-history', function() {
        $('#mr-edit-history-form').slideToggle();
    });
    
    // Patient view - Cancel edit history
    $(document).on('click', '#mr-cancel-edit-history', function() {
        $('#mr-edit-history-form').slideUp();
    });
    
    // Patient view - Add medication
    $(document).on('click', '#mr-add-patient-medication', function() {
        var row = '<div class="mr-medication-row">';
        row += '<input type="text" name="medication_name[]" placeholder="نام دارو" class="regular-text">';
        row += '<input type="text" name="medication_usage[]" placeholder="نحوه مصرف" class="regular-text">';
        row += '<button class="button mr-remove-medication">×</button>';
        row += '</div>';
        $('#mr-patient-medications-container').append(row);
    });
    
    // Patient view - Add file
    $(document).on('click', '#mr-add-patient-file', function() {
        var row = '<div class="mr-file-row">';
        row += '<input type="text" name="file_title[]" placeholder="عنوان فایل" class="regular-text">';
        row += '<input type="file" name="file_upload[]" class="mr-file-upload">';
        row += '<button class="button mr-remove-file">×</button>';
        row += '</div>';
        $('#mr-patient-files-container').append(row);
    });
    
    // Patient view - Show request record form
    $(document).on('click', '#mr-request-record-btn', function() {
        $('#mr-request-form').slideToggle();
    });
    
    // Patient view - Submit medical history (for creating record)
    $(document).on('click', '#mr-submit-medical-history', function() {
        var bloodGroup = $('[name="blood_group"]').val();
        var age = $('[name="age"]').val();
        
        var specialDiseases = [];
        $('input[name="special_diseases[]"]:checked').each(function() {
            specialDiseases.push($(this).val());
        });
        var otherDiseases = $('[name="other_diseases"]').val();
        if (otherDiseases) {
            specialDiseases.push(otherDiseases);
        }
        
        var medications = [];
        $('.mr-medication-row').each(function() {
            var name = $(this).find('[name="medication_name[]"]').val();
            var usage = $(this).find('[name="medication_usage[]"]').val();
            if (name) {
                medications.push({name: name, usage: usage});
            }
        });
        
        $.ajax({
            url: mrFrontendAjax.ajax_url,
            type: 'POST',
            data: {
                action: 'mr_save_medical_history',
                nonce: mrFrontendAjax.nonce,
                customer_id: get_current_customer_id(),
                blood_group: bloodGroup,
                special_diseases: specialDiseases.join(', '),
                age: age,
                current_medications: JSON.stringify(medications)
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
    
    // Helper functions
    function showToast(message, type) {
        var $toast = $('#mr-toast');
        $toast.text(message).addClass(type + ' show');
        
        setTimeout(function() {
            $toast.removeClass('show');
        }, 3000);
    }
    
    function toPersianDate(date) {
        if (window.persianDate) {
            return new persianDate(date).format('YYYY/MM/DD HH:mm');
        }
        return date.toLocaleDateString('fa-IR');
    }
    
    function get_current_user_id() {
        return $('body').data('current-user-id') || 0;
    }
    
    function get_current_customer_id() {
        return $('body').data('customer-id') || 0;
    }
    
    // Initialize Persian Datepicker
    if ($.fn.persianDatepicker) {
        $('.mr-datepicker').persianDatepicker({
            format: 'YYYY/MM/DD',
            autoClose: true
        });
    }
});
